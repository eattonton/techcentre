 $(function(){
    //套料板名
	$("#tb_box01").keyup(function(){
		var skey = $(this).val();
		if(skey == ""){
             return;
          }
       filterrow(0,skey);
    }).keyup();
    //材质
    $("#tb_box02").keyup(function(){
		var skey = $(this).val();
		if(skey == ""){
              return;
          }
       filterrow(1,skey);
    }).keyup();
    //厚度
    $("#tb_box03").keyup(function(){
		var skey = $(this).val();
		if(skey == ""){
              return;
          }
       filterrow(2,skey);
    }).keyup();
 })
 
 function filterrow(iclo, skey){
    	$("#nestlist tbody tr:gt(1)").hide();  //先隐藏
       	$("#nestlist tbody tr:gt(1)").each(function(){
        $(this).find("td").eq(iclo).filter(":contains('"+skey+"')").parent().show();
        });
 }