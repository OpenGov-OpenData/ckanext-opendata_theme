jQuery(document).ready(function () {
    function initColorSelector() {
        $( ".opendata-theme-color-picker").each(function( index ) {
            $(this).spectrum({
                showInput: true, // shows the color input box, which actually can take hex,  hsl, and rgb
                showPaletteOnly: true, // only shows the color selectors
                hideAfterPaletteSelect: true,
                preferredFormat: "hex", // sets the format of color input box
            });
        });
    }
    initColorSelector()
})
