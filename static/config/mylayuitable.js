var MyTable = {}

MyTable.GetRowsData = function(tableName){
    var table = layui.table
    var obj1 = {}
    var datas1 = []
    var table1 =table.cache[tableName]
    if(table1){
        for(var g=0;g<table1.length;g++){
            datas1.push(table1[g])
        }
        obj1.data = datas1
        obj1.num=datas1.length
    }
    else{
        obj1.data = []
        obj1.num=0
    }

    return obj1
}

MyTable.AddRow = function(stableName,newRow){
    var table = layui.table
    //更新行
    var nowData = MyTable.GetRowsData(stableName)
    nowData.data.push(newRow)
    table.reload(stableName,{data: nowData.data})
}

MyTable.UpdateRowData = function(row, data){
    for (var i =data.length-1; i >= 0; i--) {
        if (data[i]["_id"] == row["_id"]) {
            data[i]= row
            break
        }
    }

    return data
}

MyTable.UpdateRowDataByID = function(stableName,newData){
    var table = layui.table
    var data = table.cache[stableName]
 
    for (var i = data.length - 1; i >= 0; i--) {
        if(data[i]["_id"] == newData["_id"]){
             for(var k in newData){
                if(k == "_id") continue;
                //if(data[i].hasOwnProperty(k)){
                    data[i][k] = newData[k]
                //}
             }
        }
    }
    // console.log(data)
    table.reload(stableName,{data: data})

    return data
}

MyTable.UpdateRowDataByID2 = function(stableName,id2, newData){
    var table = layui.table
    var data = table.cache[stableName]
 
    for (var i = data.length - 1; i >= 0; i--) {
        if(data[i]["_id"] == id2){
             for(var k in newData){
                if(k == "_id2") continue;
                //if(data[i].hasOwnProperty(k)){
                    data[i][k] = newData[k]
                //}
             }
        }
    }
    //console.log(data)
    table.reload(stableName,{data: data})

    return data
}

MyTable.UpdateRowDataByChecked = function(stableName,newData){
    var table = layui.table
    var data = table.cache[stableName]
 
    for (var i = data.length - 1; i >= 0; i--) {
        if(data[i].LAY_CHECKED){
             for(var k in newData){
                if(k == "_id") continue;
                //if(data[i].hasOwnProperty(k)){
                    data[i][k] = newData[k]
               // }
             }
        }
    }

    table.reload(stableName,{data: data})

    return data
}

MyTable.RemoveRowData = function(row, data){
    for (var i = data.length - 1; i >= 0; i--) {
        console.log(row)
        if (data[i]["_id"] == row["_id"]) {
            data.splice(i, 1)
            break
        }
    }

    return data
}

MyTable.RemoveRowDataByChecked = function(stableName){
    var table = layui.table
    var data = table.cache[stableName]

    for (var i = data.length - 1; i >= 0; i--) {
        //console.log(oldData[i].LAY_CHECKED)   //LAY_TABLE_INDEX
        if(data[i].LAY_CHECKED){
            data.splice(i, 1)
        }
    }

    table.reload(stableName,{data: data})

    return data
}


MyTable.TableRowSelect = function(tableName){
    //单击行勾选checkbox事件
    $(document).on("click", "div[lay-id="+tableName+"] .layui-table-body table.layui-table tbody tr", function () {
        var index = $(this).attr('data-index');
        var tableBox = $(this).parents('.layui-table-box');
        //存在固定列
        if (tableBox.find(".layui-table-fixed.layui-table-fixed-l").length > 0) {
            tableDiv = tableBox.find(".layui-table-fixed.layui-table-fixed-l");
        } else {
            tableDiv = tableBox.find(".layui-table-body.layui-table-main");
        }
        var CheckLength = tableDiv.find("tr[data-index=" + index + "]").find(
            "td div.layui-form-checked").length;
      
        var checkCell = tableDiv.find("tr[data-index=" + index + "]").find(
            "td div.laytable-cell-checkbox div.layui-form-checkbox I");
        if (checkCell.length > 0) {
            checkCell.click();
        }
    });
 
    $(document).on("click", "div[lay-id="+tableName+"] td div.laytable-cell-checkbox div.layui-form-checkbox", function (e) {
        e.stopPropagation();
    });
}

MyTable.TableSingleSelect = function(tableName){
    //单击行勾选checkbox事件
    $(document).on("click",".layui-table-body table.layui-table tbody tr", function () {
        var index = $(this).attr('data-index');
        var tableBox = $(this).parents('.layui-table-box');
        //存在固定列
        if (tableBox.find(".layui-table-fixed.layui-table-fixed-l").length>0) {
            tableDiv = tableBox.find(".layui-table-fixed.layui-table-fixed-l");
        } else {
            tableDiv = tableBox.find(".layui-table-body.layui-table-main");
        }
        //获取已选中列并取消选中
        var trs = tableDiv.find(".layui-unselect.layui-form-checkbox.layui-form-checked").parent().parent().parent();
        for(var i = 0;i<trs.length;i++){
          var ind = $(trs[i]).attr("data-index");
          if(ind!=index){
                var checkCell = tableDiv.find("tr[data-index=" + ind + "]").find("td div.laytable-cell-checkbox div.layui-form-checkbox I");
                if (checkCell.length>0) {
                    checkCell.click();
                }
           }
        }
        //选中单击行
        var checkCell = tableDiv.find("tr[data-index=" + index + "]").find("td div.laytable-cell-checkbox div.layui-form-checkbox I");
        if(checkCell.length>0 & trs.length===1){
            checkCell.click();
        }else{
            checkCell.click();
        }
    });
    $(document).on("click", "td div.laytable-cell-checkbox div.layui-form-checkbox", function (e) {
        e.stopPropagation();
    });
}