jQuery(document).ready(function () {
    function initColorSelector() {
        $( ".opendata-theme-color-picker").each(function( index ) {
            $(this).spectrum({
                showInput: true, // shows the color input box, which actually can take hex,  hsl, and rgb
                showPaletteOnly: true, // only shows the color selectors
                hideAfterPaletteSelect: true,
                preferredFormat: "hex", // sets the format of color input box
                palette:[
                    ["#09015E","#19009B","#4B3FFF","#7589FF","#94A8FF","#000000","#323334","#616365","#939598","#FFFFFF"],
                    ["#B12525","#D33423","#885604","#C68700","#037730","#07963F","#046A9B","#0285C4","#8700D3","#A627FF"],
                    []
                ]
            });
        });
    }
    initColorSelector()
})
