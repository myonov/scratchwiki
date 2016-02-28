$(function() {
    var edit = {
        initSimpleMDE: function() {
            var simplemde = new SimpleMDE({
                element: $('#editor')[0],
                spellChecker: false,
                autoDownloadFontAwesome: false
            })

            simplemde.value(globals.data.markdown)
        },

        initSelect2: function() {
            $('#tags').select2({
                placeholder: 'Tags',
                tags: [],
                tokenSeparators: [' ', ','],
                width: '100%'
            })
            if ( globals.data.postTags.length > 0 ) {
                $('#tags').select2('val', globals.data.postTags)
            } else {
                $('#tags').select2('val', globals.data.newTags)
            }
        },

        initKeyBindings: function() {
            globals.helpers.globalTrap('ctrl+enter', function() { $('#post-form').submit() })
        }
    }

    edit.initSimpleMDE()
    edit.initSelect2()
    edit.initKeyBindings()

})