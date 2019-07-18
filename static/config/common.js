var ConfigCommon={}

ConfigCommon.GetObjFromDlg = function(dlg) {
    var newObj= {}
    var sID = "div#"+dlg
    var tbs = $(sID+" .easyui-textbox")
    $.each(tbs, function(index,item){
        var tbid = $(item).attr('id')
        newObj[tbid] = $(sID+" #"+tbid).textbox("getValue")
    })
    
    var cbbs = $("div#"+dlg+" .combobox-f")
    $.each(cbbs, function(index,item){
        var cbbid = $(item).attr('id')
        newObj[cbbid] = $(sID+" #"+cbbid).combobox("getValue")
    })

    return newObj
}

ConfigCommon.SetDlgItem = function(dlg,data){
    var sID = "div#"+dlg
    $.each(data,function(key,value){
        var sID2 = sID+" #"+key
        if($(sID2).length > 0)
        {
            var stype = $(sID2).attr("class")
            if(stype.indexOf("easyui-textbox")>= 0){
                $(sID2).textbox("setValue",value)
            }else if(stype.indexOf("combobox-f")>= 0){
                $(sID2).combobox("setValue",value)
            }
        }
        else
        {
            console.log(key+"不存在")
        }
    })
}