import * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class AcePlotView extends HTMLBoxView {
    model: AcePlot;
    protected _editor: any;
    protected _langTools: any;
    protected _modelist: any;
    protected _container: HTMLDivElement;
    initialize(): void;
    connect_signals(): void;
    render(): void;
    _update_code_from_model(): void;
    _update_print_margin(): void;
    _update_code_from_editor(): void;
    _update_theme(): void;
    _update_filename(): void;
    _update_language(): void;
    _add_annotations(): void;
    after_layout(): void;
}
export declare namespace AcePlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        code: p.Property<string>;
        language: p.Property<string>;
        filename: p.Property<string | null>;
        theme: p.Property<string>;
        annotations: p.Property<any[]>;
        print_margin: p.Property<boolean>;
        readonly: p.Property<boolean>;
    };
}
export interface AcePlot extends AcePlot.Attrs {
}
export declare class AcePlot extends HTMLBox {
    properties: AcePlot.Props;
    constructor(attrs?: Partial<AcePlot.Attrs>);
    static __module__: string;
}
