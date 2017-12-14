

function changeTraveloElementUI() {
    // change UI of select box
    tjq(".selector select").each(function() {
        var obj = tjq(this);
        if (obj.parent().children(".custom-select").length < 1) {
            obj.after("<span class='custom-select'>" + obj.children("option:selected").html() + "</span>");
            
            if (obj.hasClass("white-bg")) {
                obj.next("span.custom-select").addClass("white-bg");
            }
            if (obj.hasClass("full-width")) {
                //obj.removeClass("full-width");
                //obj.css("width", obj.parent().width() + "px");
                //obj.next("span.custom-select").css("width", obj.parent().width() + "px");
                obj.next("span.custom-select").addClass("full-width");
            }
        }
    });
    tjq("body").on("change", ".selector select", function() {
        if (tjq(this).next("span.custom-select").length > 0) {
            tjq(this).next("span.custom-select").text(tjq(this).children("option:selected").html());
        }
    });
    
    tjq("body").on("keydown", ".selector select", function() {
        if (tjq(this).next("span.custom-select").length > 0) {
            tjq(this).next("span.custom-select").text(tjq(this).children("option:selected").html());
        }
    });

    // change UI of file input
    tjq(".fileinput input[type=file]").each(function() {
        var obj = tjq(this);
        if (obj.parent().children(".custom-fileinput").length < 1) {
            obj.after('<input type="text" class="custom-fileinput" />');
            if (typeof obj.data("placeholder") != "undefined") {
                obj.next(".custom-fileinput").attr("placeholder", obj.data("placeholder"));
            }
            if (typeof obj.prop("class") != "undefined") {
                obj.next(".custom-fileinput").addClass(obj.prop("class"));
            }
            obj.parent().css("line-height", obj.outerHeight() + "px");
        }
    });

    tjq(".fileinput input[type=file]").on("change", function() {
        var fileName = this.value;
        var slashIndex = fileName.lastIndexOf("\\");
        if (slashIndex == -1) {
            slashIndex = fileName.lastIndexOf("http://www.soaptheme.com/");
        }
        if (slashIndex != -1) {
            fileName = fileName.substring(slashIndex + 1);
        }
        tjq(this).next(".custom-fileinput").val(fileName);
    });
    // checkbox
    tjq(".checkbox input[type='checkbox'], .radio input[type='radio']").each(function() {
        if (tjq(this).is(":checked")) {
            tjq(this).closest(".checkbox").addClass("checked");
            tjq(this).closest(".radio").addClass("checked");
        }
    });
    tjq(".checkbox input[type='checkbox']").bind("change", function() {
        if (tjq(this).is(":checked")) {
            tjq(this).closest(".checkbox").addClass("checked");
        } else {
            tjq(this).closest(".checkbox").removeClass("checked");
        }
    });
    //radio
    tjq(".radio input[type='radio']").bind("change", function(event, ui) {
        if (tjq(this).is(":checked")) {
            var name = tjq(this).prop("name");
            if (typeof name != "undefined") {
                tjq(".radio input[name='" + name + "']").closest('.radio').removeClass("checked");
            }
            tjq(this).closest(".radio").addClass("checked");
        }
    });


    

}

tjq(document).ready(function() {
    changeTraveloElementUI();
});

