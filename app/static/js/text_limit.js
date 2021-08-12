(function($){
    var count = 20;
   $('.text_limit').each(function(){
       var thisText = $(this).text();
       var textLength = thisText.length;
       if(textLength > count){
       var showText = thisText.substring(0,
       count);
       var insertText = showText += '…';
       $(this).html(insertText);
     };
   });
})(jQuery);
