/*Loading イメージ表示関数
　引数： msg 画面に表示する文章*/

function dispLoading(msg){
if(msg == undefined){
    msg = "";
    }
    //画面表示メッセージ
    var dispMsg = "<div class='loadingMsg'>" + msg + "</div>";
    //ローディング画像が表示されていない場合のみ出力
    if($("#loading").length == 0){
        $("body").append("<div id='loading'>" + dispMsg + "</div>");
    }
}

/*Loading イメージ削除関数*/
function removeLoading(){
    $("#loading").remove();
}