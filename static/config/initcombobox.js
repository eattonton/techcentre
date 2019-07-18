var ConfigCombobox={}
//加载配置
function getOptions(value, call) {
    return $(value).map(call).get();
}

ConfigCombobox.loadFormatter = function(name, arr1, formatter,title) {
    $('#' + name).combobox({
        data: getOptions(arr1, formatter),
        textField: 't',
        valueField: 'v',
        label: title==undefined?name:title
    });
}

ConfigCombobox.loadFromArray = function(name,arr1,title){
    var data1 = $(arr1).map(ConfigCombobox.objFromArr).get();

    $('#' + name).combobox({
        data: data1,
        textField: 't',
        valueField: 'v',
        label: title==undefined?name:title
    });
}

ConfigCombobox.objFromArr = function(idx, val){
  return {
    t:val,
    v:val
  }
}

ConfigCombobox.workTeamFromArr = function(idx, val) {
    return {
        t: val.name,
        v: val.name,
        施工队: val.施工队
    }
}

ConfigCombobox.shipClassFromArr = function(idx, val) {
    return {
        t: val.name,
        v: val.name,
        考试位置: val.考试位置
    }
}

ConfigCombobox.weldMethodFromArr = function(idx, val) {
    return {
        t: val[1] + "," + val[2],
        v: val[1] + "," + val[2]
    }
}
