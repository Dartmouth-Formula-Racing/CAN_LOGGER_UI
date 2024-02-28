var _a;
import { Control, ControlView } from '@bokehjs/models/widgets/control';
import { Tooltip } from '@bokehjs/models/ui/tooltip';
import { build_view } from '@bokehjs/core/build_views';
import { div, label } from '@bokehjs/core/dom';
import inputs_css, * as inputs from '@bokehjs/styles/widgets/inputs.css';
import icons_css from '@bokehjs/styles/icons.css';
class TooltipIconView extends ControlView {
    *controls() { }
    *children() {
        yield* super.children();
        yield this.description;
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        const { description } = this.model;
        this.description = await build_view(description, { parent: this });
    }
    remove() {
        this.description?.remove();
        super.remove();
    }
    stylesheets() {
        return [...super.stylesheets(), inputs_css, icons_css];
    }
    render() {
        super.render();
        const icon_el = div({ class: inputs.icon });
        this.desc_el = div({ class: inputs.description }, icon_el);
        const { desc_el, description } = this;
        description.model.target = desc_el;
        let persistent = false;
        const toggle = (visible) => {
            description.model.setv({
                visible,
                closable: persistent,
            });
            icon_el.classList.toggle(inputs.opaque, visible && persistent);
        };
        this.on_change(description.model.properties.visible, () => {
            const { visible } = description.model;
            if (!visible) {
                persistent = false;
            }
            toggle(visible);
        });
        desc_el.addEventListener('mouseenter', () => {
            toggle(true);
        });
        desc_el.addEventListener('mouseleave', () => {
            if (!persistent)
                toggle(false);
        });
        document.addEventListener('mousedown', (event) => {
            const path = event.composedPath();
            if (path.includes(description.el)) {
                return;
            }
            else if (path.includes(desc_el)) {
                persistent = !persistent;
                toggle(persistent);
            }
            else {
                persistent = false;
                toggle(false);
            }
        });
        window.addEventListener('blur', () => {
            persistent = false;
            toggle(false);
        });
        // Label to get highlight when icon is hovered
        this.shadow_el.appendChild(label(this.desc_el));
    }
    change_input() { }
}
TooltipIconView.__name__ = "TooltipIconView";
export { TooltipIconView };
class TooltipIcon extends Control {
    constructor(attrs) {
        super(attrs);
    }
}
_a = TooltipIcon;
TooltipIcon.__name__ = "TooltipIcon";
TooltipIcon.__module__ = 'panel.models.widgets';
(() => {
    _a.prototype.default_view = TooltipIconView;
    _a.define(({ Ref }) => ({
        description: [Ref(Tooltip), new Tooltip()],
    }));
})();
export { TooltipIcon };
//# sourceMappingURL=tooltip_icon.js.map