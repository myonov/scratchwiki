var globals = globals || {}

globals['helpers'] = {
    globalTrap: function(cmd, callback) {
        Mousetrap.bind(cmd, callback)
        ; ['input', 'textarea'].forEach(function(selector, _) {
            $(selector).each(function(_, el) {
                Mousetrap(el).bind(cmd, callback)
            })
        })
    }
}