/* To use this script, simply add the script and dependencies to the Media
 * defination of ModelAdmin:

class UserAccessAggregateOptions(admin.ModelAdmin):
    list_display = ...
    list_filter = ...
    class Media:
        js = [
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js',
            '{}}js/admin_fix_long_list_filter.js?show=active'.format(settings.MEDIA_URL),
        ]
        css = {'all': 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css'}


 * Options:
 * You can pass in options to the script

    class Media:
        js = map (lambda p: settings.STATIC_URL+"js/"+p, (
            'long_list_filter.js?show=all&height=200',
        ))
 *
 * Available options:
 * threshold: when a list_filter is taller than {{ threshold }}, the script will
 *   will be applied on it. default is 300
 * show: choices are "all", "none" and "active", default is active
 *   all means all options will be displayed
 *   none means only the "All" option will show up
 *   active means only the "All" and selected option will show up
 * height: If you set show=all, we'll set the heighth of the list_filter to
 *   {{ height }}, default is 100
 **/

jQuery(document).ready(function($) {
    function get_query_variable(variable) {
        var query = '';
        $('script').each(function(){
            if (!query){
                var src = $(this).attr('src');
                if (src && src.indexOf('long_list_filter.js') != -1){
                    query = src.split('?')[1]
                }
            }
        });
        if (query){
            var vars = query.split("&");
            for (var i=0;i<vars.length;i++) {
                var pair = vars[i].split("=");
                if (pair[0] == variable) {
                    return pair[1];
                }
            }
        }
        return null;
    }
    var base_selector = 'long_list_filter_#num#';
    var base_ul_selector = 'long_list_filter_ul_#num#';
    var HEIGHT = get_query_variable('height') || 100;
    var THRESHOLD = get_query_variable('threshold') || 300;
    var SHOW = get_query_variable('show') || 'active'; //  all or active or none
    
    $('ul', '#changelist-filter').each(function(n){
        if ($(this).height() > THRESHOLD){
            var ul = $(this);
            
            if (SHOW=='active'){
                // :gt(0) makes sure All is always displayed
                $('li', ul).filter(':gt(0)').not('.selected').hide();
            }
            if (SHOW=='none'){
                $('li', ul).filter(':gt(0)').hide();
            }
            if (SHOW=='all'){
                ul.height(HEIGHT)
            }

            $(this).css({'overflow-y':'auto', 'overflow-x':'hidden', 'list-style':'none'});
            $('li', this).each(function(){
                $(this).attr('title', $.trim($(this).text()));
            });
            var current_selector = base_selector.replace('#num#', n);
            var current_ul_selector = base_ul_selector.replace('#num#', n);
            $(this).attr('id', current_ul_selector);
            $(this).before(
                '<div><input id="#id#" placeholder="Start typing..." class="long-list-filter-input"></div>'.replace('#id#', current_selector)
            );
            $('#' + current_selector).css('margin-left','10px');
            var items = $('li', this);
            var availableOptions = [];
            items.each(function(){
                var val = $.trim($(this).text());
                availableOptions.push(val)
            });
            $('li', this).attr('title', 'Click to remove').first().attr('title', 'Clear this filter');;
            
            $('li', this).tooltip();
            
            var ac = $("#" + current_selector).autocomplete({
                source: availableOptions,
                position: {collision: "fit none"},
                minLength: 0,
                select: function(event, ui){
                    var value_slected = ui.item.value;
                    $('li', '#' + current_ul_selector).each(function(){
                        if($.trim($(this).text())==value_slected){
                            location.href = $('a', $(this)).attr('href')
                        }
                    })
                },
                open: function(){
                    $(this).autocomplete('widget').css('z-index', 100000);
                    return false;
                }
            });


        }
    });

    sync_display_of_input();
    //We need to toggle the inputs as "show/hide" is clicked
    $('h2', '#changelist-filter').click(function(){
        setTimeout('sync_display_of_input()', 100);
        setTimeout('sync_display_of_input()', 200);
        setTimeout('sync_display_of_input()', 300);
        setTimeout('sync_display_of_input()', 400);
        setTimeout('sync_display_of_input()', 500);
        setTimeout('sync_display_of_input()', 1000);
    })

});

function sync_display_of_input(){
    var display = $('h3', '#changelist-filter').css('display');
    $('.long-list-filter-input').css('display', display)
}
