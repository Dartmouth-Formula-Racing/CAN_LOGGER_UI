var _a;
import { div } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
const normalizeNative = (nativeRange) => {
    // document.getSelection model has properties startContainer and endContainer
    // shadow.getSelection model has baseNode and focusNode
    // Unify formats to always look like document.getSelection
    if (nativeRange) {
        const range = nativeRange;
        if (range.baseNode) {
            range.startContainer = nativeRange.baseNode;
            range.endContainer = nativeRange.focusNode;
            range.startOffset = nativeRange.baseOffset;
            range.endOffset = nativeRange.focusOffset;
            if (range.endOffset < range.startOffset) {
                range.startContainer = nativeRange.focusNode;
                range.endContainer = nativeRange.baseNode;
                range.startOffset = nativeRange.focusOffset;
                range.endOffset = nativeRange.baseOffset;
            }
        }
        if (range.startContainer) {
            return {
                start: { node: range.startContainer, offset: range.startOffset },
                end: { node: range.endContainer, offset: range.endOffset },
                native: range
            };
        }
    }
    return null;
};
class QuillInputView extends HTMLBoxView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.disabled.change, () => this.quill.enable(!this.model.disabled));
        this.connect(this.model.properties.visible.change, () => {
            if (this.model.visible)
                this.container.style.visibility = 'visible';
        });
        this.connect(this.model.properties.text.change, () => {
            if (this._editing)
                return;
            this._editing = true;
            this.quill.enable(false);
            this.quill.setContents([]);
            this.quill.clipboard.dangerouslyPasteHTML(this.model.text);
            this.quill.enable(!this.model.disabled);
            this._editing = false;
        });
        const { mode, toolbar, placeholder } = this.model.properties;
        this.on_change([placeholder], () => {
            this.quill.root.setAttribute('data-placeholder', this.model.placeholder);
        });
        this.on_change([mode, toolbar], () => {
            this.render();
            this._layout_toolbar();
        });
    }
    _layout_toolbar() {
        if (this._toolbar == null) {
            this.el.style.removeProperty('padding-top');
        }
        else {
            const height = this._toolbar.getBoundingClientRect().height + 1;
            this.el.style.paddingTop = height + "px";
            this._toolbar.style.marginTop = -height + "px";
        }
    }
    render() {
        super.render();
        this.container = div({ style: "visibility: hidden;" });
        this.shadow_el.appendChild(this.container);
        const theme = (this.model.mode === 'bubble') ? 'bubble' : 'snow';
        this.watch_stylesheets();
        this.quill = new window.Quill(this.container, {
            modules: {
                toolbar: this.model.toolbar
            },
            readOnly: true,
            placeholder: this.model.placeholder,
            theme: theme
        });
        // Hack Quill and replace document.getSelection with shadow.getSelection
        // see https://stackoverflow.com/questions/67914657/quill-editor-inside-shadow-dom/67944380#67944380
        this.quill.selection.getNativeRange = () => {
            const selection = this.shadow_el.getSelection();
            const range = normalizeNative(selection);
            return range;
        };
        this._editor = this.shadow_el.querySelector('.ql-editor');
        this._toolbar = this.shadow_el.querySelector('.ql-toolbar');
        const delta = this.quill.clipboard.convert(this.model.text);
        this.quill.setContents(delta);
        this.quill.on('text-change', () => {
            if (this._editing)
                return;
            this._editing = true;
            this.model.text = this._editor.innerHTML;
            this._editing = false;
        });
        if (!this.model.disabled)
            this.quill.enable(!this.model.disabled);
        document.addEventListener("selectionchange", (..._args) => {
            // Update selection and some other properties
            this.quill.selection.update();
        });
    }
    style_redraw() {
        if (this.model.visible)
            this.container.style.visibility = 'visible';
        const delta = this.quill.clipboard.convert(this.model.text);
        this.quill.setContents(delta);
        this.invalidate_layout();
    }
    after_layout() {
        super.after_layout();
        this._layout_toolbar();
    }
}
QuillInputView.__name__ = "QuillInputView";
export { QuillInputView };
class QuillInput extends HTMLBox {
    constructor(attrs) {
        super(attrs);
    }
}
_a = QuillInput;
QuillInput.__name__ = "QuillInput";
QuillInput.__module__ = "panel.models.quill";
(() => {
    _a.prototype.default_view = QuillInputView;
    _a.define(({ Any, String }) => ({
        mode: [String, 'toolbar'],
        placeholder: [String, ''],
        text: [String, ''],
        toolbar: [Any, null],
    }));
    _a.override({
        height: 300
    });
})();
export { QuillInput };
//# sourceMappingURL=quill.js.map