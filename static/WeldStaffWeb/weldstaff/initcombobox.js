//加载配置
function getOptions(value, call) {
    return $(value).map(call).get();
}

function loadCombobox1(name, arr1, formatter,title) {
    $('#' + name).combobox({
        data: getOptions(arr1, formatter),
        textField: 't',
        valueField: 'v',
        label: title==undefined?name:title
    });
}

function loadComboboxFromArray(name,arr1,title){
    var data1 = $(arr1).map(objFromArr).get();

    $('#' + name).combobox({
        data: data1,
        textField: 't',
        valueField: 'v',
        label: title==undefined?name:title
    });
}

var objFromArr = function(idx, val){
  return {
    t:val,
    v:val
  }
}

var workTeamFromArr = function(idx, val) {
    return {
        t: val.name,
        v: val.name,
        施工队: val.施工队
    }
}

var shipClassFromArr = function(idx, val) {
    return {
        t: val.name,
        v: val.name,
        考试位置: val.考试位置
    }
}

var weldMethodFromArr = function(idx, val) {
    return {
        t: val[1] + "," + val[2],
        v: val[1] + "," + val[2]
    }
}
