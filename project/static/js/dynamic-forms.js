$(function() {

    $('form input').on('keypress', function(e) {
        return e.which !== 13;
    });

    function parse_inc(match) {
        var i = parseInt(match);
        i++;
        return String(i);
    }
    // Remove button click
    $(document).on(
        'click',
        '[data-role="dynamic-fields"] > .form-custom [data-role="remove"]',
        function(e) {
            e.preventDefault();
            $(this).closest('.form-custom').remove();
        }
    );
    // Add button click
    $(document).on(
        'click',
        '[data-role="dynamic-fields"] > .form-custom [data-role="add"]',
        function(e) {
            e.preventDefault();
            var container = $(this).closest('[data-role="dynamic-fields"]');
            var new_field_group = container.children().filter('.form-custom:last-child').clone();
            new_field_group.find('input, select, label').each(function(){
                if (!$(this).is('label')) {
                    if ($(this).is('select')){
                        $(this).val('0');
                    } else { $(this).val(''); }
                    var old_name = $(this).attr('name');
                    var new_name = old_name.replace(/\d{1,2}/, parse_inc);
                    $(this).attr('name', new_name);
                    $(this).attr('id', new_name);
                } else {
                    var old_for = $(this).attr('for');
                    var new_for = old_for.replace(/\d{1,2}/, parse_inc);
                    $(this).attr('for', new_for);
                }
            });
            new_field_group.find('.errors').each(function(){
                $(this).remove();
            });
            container.append(new_field_group);
        }
    );
    // make all but last button into remove button
    $(".dyn-form-container").each(
        function() {
            $(this).find(".dyn-buttons").not(':last').each(
                function() {
                    $(this).find('button').each(
                        function () {
                            if ($(this).data('role') === 'remove') {
                                $(this).show();
                            }
                            else {
                                $(this).hide();
                            }
                        }
                    );
                }
            );
        }
    );
    $('.form-custom').each(
        function () {
            var instForm = $(this).find('.instrumento:first');
            if ($(this).find('.rol-pista:first').val() !== 'Interpretación musical') {
                instForm.val(1);
                var inst = $(this).find('.instrumento:first');
                inst.css('visibility', 'hidden');
                $("label[for='"+inst.attr('id')+"']").css('visibility', 'hidden');
            }
            else {
                var inst = $(this).find('.instrumento:first');
                inst.css('visibility', 'visible');
                $("label[for='"+inst.attr('id')+"']").css('visibility', 'visible');
            }
        }
    );
    // Only allow instrument selection when the rol is set as Interpretación musical'
    $(document).on('click', function() {
        $('.form-custom').on('change',
            function () {
                var instForm = $(this).find('.instrumento:first');
                if ($(this).find('.rol-pista:first').val() !== 'Interpretación musical') {
                    instForm.val(1);
                    var inst = $(this).find('.instrumento:first');
                    inst.css('visibility', 'hidden');
                    $("label[for='"+inst.attr('id')+"']").css('visibility', 'hidden');
                }
                else {
                    var inst = $(this).find('.instrumento:first');
                    inst.css('visibility', 'visible');
                    $("label[for='"+inst.attr('id')+"']").css('visibility', 'visible');
                }
            }
        );
    });

    $('.pull-down').each(function() {
        var $this = $(this);
        $this.css('margin-top', $this.parent().height() - $this.height())
    });
    $('#references').attr('data-toggle', 'collapse');
    $('#references').attr('data-target', '#references-collapsible');
});


