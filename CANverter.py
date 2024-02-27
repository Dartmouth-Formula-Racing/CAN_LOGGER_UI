import cantools
import re
import pandas as pd
import numpy as np

class CANverter():
    #CONSTANTS
    SOCKET_CAN_LINE_PATTERN = re.compile(r"(\d+)#([0-9A-F#]{3}|[0-9A-F#]{8})#([0-9A-F]+)")
    
    DPS_BASE = 3
    LOGGING_BASE = 1

    def __init__(self, dbc_file_path : str):
        self.dbcFilePath = dbc_file_path
        self.signalList = ['Time']
        self.displaySignalList = ['Time']
        self.signalUnitList = ['(ms)']
        self.signalMinList = [None]
        self.signalMaxList = [None]
        self.dpsList = [3]
        self.dbc = cantools.database.load_file(dbc_file_path)
        self.save_dbc_signal_data()
        for i in range(len(self.signalList)) :
            self.displaySignalList[i] += " " + self.signalUnitList[i]
        
    def __str__(self):
        return self.dbcFilePath.split("/")[-1]

    def get_encoded_pattern(self, row : str):
        # Get tokens
        tokens = CANverter.SOCKET_CAN_LINE_PATTERN.search(row).groups()
        # Return tokens in correct format
        timestamp = int(tokens[0])
        identifier = int(tokens[1],16)
        dataPacket = bytearray.fromhex(tokens[2])
        # Return packet
        return (timestamp, identifier, dataPacket)


    def get_decoded_values(self, identifier, data, aggregatedValues):
        there_is_data = False
        #decode data
        try:
            decodedMessage = self.dbc.decode_message(identifier, data, decode_choices=False)
            #Iterate through decoded signals and ensure within min and max
            for (signalName, signalValue) in decodedMessage.items():
                if signalName in self.signalList:
                    signalIndex = self.signalList.index(signalName)
                    signalMin = self.signalMinList[signalIndex]
                    signalMax = self.signalMaxList[signalIndex]
                    
                    if  ((signalMin == None or signalValue >= signalMin) and (signalMax == None or signalValue <= signalMax)):
                        dps = self.dpsList[signalIndex]
                        if dps != None:
                            try:
                                signalValue = round(float(signalValue), dps)
                            except:
                                pass
                        aggregatedValues[signalIndex].append(signalValue) #save data if within boundary
                        there_is_data = True
        except Exception as ex:
            pass

        return there_is_data    
        
    def save_dbc_signal_data(self):
        identifierList = [] #CAN Identifiers
        
        #iterate through dbc object to get identifier list
        for dbcMessage in self.dbc.messages:
            messageList = str(dbcMessage).split(',')
            identifierList.append(int(messageList[1],0))
        
        #sort it
        identifierList.sort() 
                
        #Iterate through identifier data and saving the signal data
        for identifier in identifierList:
            frameID = self.dbc.get_message_by_frame_id(identifier)
            signalSet = frameID.signals

            if len(signalSet) > 0:
                for signal in signalSet:
                    if signal.is_multiplexer == False:
                        signalComment = signal.comment
                        log = CANverter.LOGGING_BASE
                        try:
                            log = int(re.findall("LOG = (d{1})",signalComment)[0])
                        except: 
                            pass
                        #Updating dbc signal data of CANVerter data
                        if log >=1:
                            self.signalList.append(str(signal.name))
                            self.displaySignalList.append(str(signal.name).replace("_"," "))
                            self.signalMinList.append(signal.minimum)
                            self.signalMaxList.append(signal.maximum)
                            if signal.unit != None:
                                self.signalUnitList.append("("+signal.unit+")")
                            else:
                                self.signalUnitList.append('')
                            try:
                                dps = int(re.findall("DPS = (\d{2}|\d{1})",signalComment)[0])
                                self.dpsList(dps)
                            except:
                                self.dpsList.append(CANverter.DPS_BASE)
                                
    def log_to_dataframe(self, logFileName : str):
        #Open log file for reading
        with open (logFileName, "r",encoding="utf8") as logFile:
            #Combine signal name and unit for column title
            dataframeRows = [] #Dataframe rows
            
            averagedValuesList = [np.nan] * len(self.signalList) #Avg values if signal freq > 1000 Hz
            currentValuesList = [ [] for _ in range(len(self.signalList)) ] #Current decoded values list

            there_is_data_in_curr_list = False
            row = logFile.readline()
            try:
                (lastTimestamp, identifier, data) = self.get_encoded_pattern(row) #Get first line
                there_is_data_in_curr_list = self.get_decoded_values(identifier, data, currentValuesList) #Decode first line
            except:
                lastTimestamp = -1 #First line was invalid

            row = logFile.readline()
            while (row):
                try:
                    (timestamp, identifier, data) = self.get_encoded_pattern(row) #get line timestamp
                    if (lastTimestamp != timestamp and there_is_data_in_curr_list): #if timestamp is different we save the row for the dataframe
                        averagedValuesList[0] = lastTimestamp #add timestamp to row
                        lastTimestamp = timestamp

                        for i, values in enumerate(currentValuesList):
                            numOfValues = len(values)
                            if numOfValues > 0:
                                averageValue = float(values[-1])
                                try:
                                    if numOfValues > 1:
                                            averageValue = float(sum(values)/numOfValues)
                                    if self.dpsList[i] != 'None':
                                        averageValue = round(averageValue, self.dpsList[i])
                                except:
                                    pass
                                averagedValuesList[i] = averageValue
                        dataframeRows.append(averagedValuesList.copy()) #append to dataframe rows
                        currentValuesList = [ [] for _ in range(len(self.signalList)) ] #clear our data lists
                        averagedValuesList = [np.nan] * len(currentValuesList)
                        there_is_data_in_curr_list = False

                    there_is_data_in_curr_list = self.get_decoded_values(identifier, data, currentValuesList) or there_is_data_in_curr_list
                    row = logFile.readline()
                except Exception as ex:
                    # print(ex)
                    pass #invalid line
            
            try:
                if (there_is_data_in_curr_list): #if timestamp is different we save the row for the dataframe
                    averagedValuesList[0] = lastTimestamp #add timestamp to row

                    for i, values in enumerate(currentValuesList):
                        numOfValues = len(values)
                        if numOfValues > 0:
                            averageValue = float(values[-1])
                            try:
                                if numOfValues > 1:
                                        averageValue = float(sum(values)/numOfValues)
                                if self.dpsList[i] != 'None':
                                    averageValue = round(averageValue, self.dpsList[i])
                            except:
                                pass
                            averagedValuesList[i] = averageValue
                    dataframeRows.append(averagedValuesList.copy()) #append to dataframe rows
            except Exception as ex:
                # print(ex)
                pass #invalid line
            
        logFile.close()
        
        return pd.DataFrame(dataframeRows, columns = self.displaySignalList) #return decoded data in dataframe


    def decode_message_stream(self, socketCANLine):
        try:
            (timestamp, identifier, data) = self.get_encoded_pattern(socketCANLine)
            valuesList = [np.nan] * len(self.signalList)
            valuesList[0] = timestamp

            decodedMessage = self.dbc.decode_message(identifier, data, decode_choices=False)
            for (signalName, signalValue) in decodedMessage.items():
                if signalName in self.signalList:
                    signalIndex = self.signalList.index(signalName)
                    signalMin = self.signalMinList[signalIndex]
                    signalMax = self.signalMaxList[signalIndex]
                    
                    if  ((signalMin == None or signalValue >= signalMin) and (signalMax == None or signalValue <= signalMax)):
                        dps = self.dpsList[signalIndex]
                        if dps != None:
                            try:
                                signalValue = round(float(signalValue), dps)
                            except:
                                pass
                        valuesList[signalIndex] = signalValue
                            
            return pd.DataFrame([valuesList], columns = self.displaySignalList)
        except:
            return pd.DataFrame()

if __name__ == "__main__":
    # Sample code on how to use
    # time_series_canverter = CANverter("./dbc/time_series.dbc")
    # df = time_series_canverter.log_to_dataframe("./test_messages/CAN_00012.log")
    # print(df.head)
    # df.to_csv( "./CAN_00012.csv")

    message_canverter = CANverter("./dbc/message.dbc")
    df = message_canverter.log_to_dataframe("./test_messages/POST_Faults.log")
    print(df.head)

    # message_canverter = CANverter("./dbc/message.dbc")
    # dfsingle = message_canverter.decode_message_stream("(0000282789) X 000000AB#FF00000000000000")
    # print(dfsingle.head)
    # dfsingle.to_csv( "./POST_Faults.csv")
