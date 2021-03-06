$(document).ready(function(){
    $('.taggable').each(function(){
        $(this).select2({
            tags: $(this).data("tags") ? $(this).data("tags").split(",") : [],
            tokenSeparators: [",", " "],
            width: "element"
        });
    });

    $('.select2able').each(function(){
        $("#" + $(this).attr('id')).select2({width: "element"});
    });
});

function encodeTag(tag_name){
    /* This takes a tag_name like "alpha@beta#gamma.delta-epsilon" and converts
     * it to a valid CSS identifier by escaping non alphabetic/numeric characters with
     * "-ASCII_CODE-", with a special case for the "-" character, which is
     * replaced with "--".
     *
     * It also prefixes the tag with "tag-"
     *
     * So "foo@ba-r" would become "tag-foo-64-ba--r"
     */

    // we prefix the encoded tag with "tag-"
    var encoded_tag = ["tag-"];
    for(var i = 0; i < tag_name.length; i++){
        var c = tag_name.charAt(i);
        if(c == "-"){
            // dashes are replaced with double dashes
            encoded_tag.push("--");
        } else if(c.match(/[A-Za-z0-9]/)){
            // we don't have to do anything special for these characters
            encoded_tag.push(c);
        } else {
            // non alphanumeric characters are replace by "-ASCII_CODE_VALUE-"
            encoded_tag.push("-" + c.charCodeAt(0) + "-");
        }
    }

    return encoded_tag.join("");
}

function decodeTag(encoded_tag){
    /* This decodes a tag name generated by encodedTag */
    var decoded_tag = [];
    // remove the "tag-" prefix
    encoded_tag = encoded_tag.slice(4);
    for(var i = 0; i < encoded_tag.length; i++){
        var c = encoded_tag.charAt(i);
        if(c.match(/[A-Za-z0-9]/)){
            // we don't have to do anything special for these characters
            decoded_tag.push(c);
        } else if(c == "-" && encoded_tag.charAt(i+1) == "-"){
            // if the current character is a dash, and the next is a dash too,
            // that means the original character was a dash
            decoded_tag.push("-");
            // we need to bump up the index since the extra character was part
            // of the escape sequence
            i++;
        } else {
            // this means we hit a dash followed by a number, followed by another dash
            // so find the ending dash
            var ending_position = encoded_tag.indexOf("-", i+1);
            // the number between the dashes is the ascii value of the character
            var ascii_value = parseInt(encoded_tag.slice(i+1, ending_position), 10);
            // add the decoded ascii value to our decoded tag
            decoded_tag.push(String.fromCharCode(ascii_value));
            // bump up the index to where the last dash was since it was part
            // of the escape sequence
            i = ending_position;
        }
    }

    return decoded_tag.join("");
}
