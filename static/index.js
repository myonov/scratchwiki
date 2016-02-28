$(function() {
    var index = {
        initSelect2: function() {
            $('#search').select2({
                placeholder: 'Search tags',
                tags: true,
                tokenSeparators: [' ', ','],
                width: '100%'
            });

            $('#search').select2('val', globals.data['tags'])
        },

        _toggleMeta: function(showContextMenu) {
            showContextMenu = parseInt(showContextMenu)
            if ( showContextMenu ) {
                $('.meta-entry').css({
                    display: ''
                })
                $('.post-buttons').css({
                    display: ''
                })
                $('.entry').css({
                    border: '1px solid #ddd',
                    'margin-top': 20,
                    'padding': 20
                })
                $('.entry').addClass('well')
                $('.entry').addClass('well-sm')
            } else {
                $('.meta-entry').css({
                    display: 'none'
                })
                $('.post-buttons').css({
                    display: 'none'
                })
                $('.entry').css({
                    border: 'none',
                    'margin-top': 0,
                    'padding': 0
                })
                $('.well').each(function(idx, el) { $(el).removeClass('well') })
                $('.well').each(function(idx, el) { $(el).removeClass('well-sm') })
            }
        },

        initContextMenu: function() {
            var callback = function() {
                var showOrHide = sessionStorage.getItem('showContextMenu') || 1
                showOrHide = 1 - showOrHide
                sessionStorage.setItem('showContextMenu', showOrHide)
                index._toggleMeta(showOrHide)
            }
            globals.helpers.globalTrap('alt+h', callback)

            index._toggleMeta(sessionStorage.getItem('showContextMenu') || 1)
        },

        initConfirmationOnDelete: function() {
            $('[data-toggle="confirmation"]').confirmation({
                placement: 'top',
                onConfirm: function(event, element) {
                    window.location = $(element).attr('href')
                }
            })
        },

        initNewPosts: function() {
            $('#new-btn').click(function() {
                location.href = (
                    globals.data['newPostUrl'] + '?tags=' + encodeURIComponent($('#search').val())
                )
            })
        },

        initTagButtons: function() {
            $('.tag-buttons a').click(function(e) {
                var currentTags, $that, newTag

                e.preventDefault()
                currentTags = $('#search').select2('val')
                $that = $(this)
                newTag = $that.attr('aria-label')
                currentTags.push(newTag)
                $('#search').select2('val', currentTags)
            })
        },

        initKeyBindings: function() {
            globals.helpers.globalTrap('alt+n', function() { $('#new-btn').trigger('click') })
            globals.helpers.globalTrap('ctrl+enter', function() { $('#search-btn').trigger('click') })
            globals.helpers.globalTrap('alt+k', function() { $('#nav-btn-prev').trigger('click') })
            globals.helpers.globalTrap('alt+l', function() { $('#nav-btn-next').trigger('click') })
        },

        initSearchButton: function() {
            $('#search-btn').click(function() {
                var tags = $('#search').select2('val').join(',')

                location.href = globals.data['searchUrl'] + '?tags=' + encodeURIComponent(tags)
            })
        },

        initNavButtons: function() {
            $('.nav-btn').click(function(e) {
                var term, prefix, $that = $(this)

                if ( $that.hasClass('disabled') ) {
                    return
                }

                term = /([&?])page=(\d+)/
                if ( location.href.match(term) != null ) {
                    location.href = location.href.replace(term, function(match, p1, p2) {
                        return p1 + 'page=' + $that.data('page')
                    })
                } else {
                    if ( location.href.indexOf('?') != -1 ) {
                        prefix = '&'
                    } else {
                        prefix = '?'
                    }
                    location.href = location.href + prefix + 'page=' + $that.data('page')
                }
            })
        }

    }

    index.initSelect2()
    index.initContextMenu()
    index.initConfirmationOnDelete()
    index.initNewPosts()
    index.initTagButtons()
    index.initKeyBindings()
    index.initSearchButton()
    index.initNavButtons()

})