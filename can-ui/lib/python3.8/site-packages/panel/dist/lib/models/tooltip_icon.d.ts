import { Control, ControlView } from '@bokehjs/models/widgets/control';
import { Tooltip, TooltipView } from '@bokehjs/models/ui/tooltip';
import { IterViews } from '@bokehjs/core/build_views';
import { StyleSheetLike } from '@bokehjs/core/dom';
import * as p from '@bokehjs/core/properties';
export declare class TooltipIconView extends ControlView {
    model: TooltipIcon;
    protected description: TooltipView;
    protected desc_el: HTMLElement;
    controls(): Generator<never, void, unknown>;
    children(): IterViews;
    lazy_initialize(): Promise<void>;
    remove(): void;
    stylesheets(): StyleSheetLike[];
    render(): void;
    change_input(): void;
}
export declare namespace TooltipIcon {
    type Attrs = p.AttrsOf<Props>;
    type Props = Control.Props & {
        description: p.Property<Tooltip>;
    };
}
export interface TooltipIcon extends TooltipIcon.Attrs {
}
export declare class TooltipIcon extends Control {
    properties: TooltipIcon.Props;
    __view_type__: TooltipIconView;
    static __module__: string;
    constructor(attrs?: Partial<TooltipIcon.Attrs>);
}
