function genBaseInput(form) {
  var define = function(cell, key, value) {
    if (_.isUndefined(cell[key])) {
      cell[key] = value;
    }
  };
  return form.map(function (cell) {
    define(cell, "align", "center");
    define(cell, "title", cell.field);
    define(cell, "width", 100);
    define(cell, "viewName", "textbox");
    define(cell, "required", false);
    return _.clone(cell);
  });
}
function genFormItem(form) {
  return form.map(function (cell) {
    return {
      id: cell.id,
      viewName: cell.viewName,
      labelAlign: cell.labelAlign || "left",
      type: "text",
      value: cell.default,
      label: cell.label,
      required: cell.required,
      input: cell.input || true,
      column: cell.column || {}
    };
  });
}

var WeldIputForm = [
  { field: "焊工编号" },
  {
    field: "姓名",
    sortable: true
  },
  {
    field: "身份证",
    sortable: true
  },
  {
    viewName: "combobox",
    field: "性别",
    width:40
  },
  {
    viewName: "combobox",
    field: "船级社",
    width:60
  },
  {
    viewName: "combobox",
    field: "工区",
    title: "所属工区"
  },
  {
    viewName: "combobox",
    field: "施工队",
    sortable: true
  },
  {
    viewName: "combobox",
    field: "焊接方法1",
    title: "焊接方法1",
    sortable: true
  },
  {
    viewName: "combobox",
    field: "焊接方法2",
    title: "焊接方法2",
    sortable: true
  },
  {
    viewName: "combobox",
    field: "试件形式",
    sortable: true
  },
  {
    field: "合格位置",
    title: "合格位置",
    sortable: true
  },
  {
    field: "可焊位置",
    title: "可焊位置",
    sortable: true
  },
  {
    field: "板厚",
    title: "可焊板厚",
    sortable: true
  },
  {
    field: "管厚",
    title: "可焊管厚",
  },
  {
    field: "管径",
    title: "可焊管径",
  },
  {
    viewName: "combobox",
    field: "母材性质"
  },
  {
    field: "填充金属",
    title: "填充金属类型"
  },
  {
    viewName: "combobox",
    field: "接头形式",
    width: 120
  },
  {
    viewName: "datebox",
    field: "代用证日期"
  },
  {
    viewName: "datebox",
    field: "代用证到期"
  },
  // {
  //   field: "钢印"
  // },
  {
    field: "照片",
    input: null
  }
];

function formatStr(str) {
  return function(item) {
    return str;
  };
}

//CCS证书申请
var WeldIputCCSForm = [
  { field: "证书类型", width: 60 },
  { field: "焊工编号" },
  {
    field: "姓名",
    sortable: true
  },
  {
    field: "身份证",
    sortable: true
  },
  {
    viewName: "combobox",
    field: "性别",
    width:35
  },
  {
    field: "工厂名称",
    width: 70
  },
  {
    field: "文化程度",
    width: 50,
    input: null
  },
  {
    field:"焊接工作时间",
    title: "从事焊接连续工作时间",
    width: 100,
    input: null
  },
  {
    field: "邮政编码",
    width: 60
  },
  {
    field: "联系地址",
    width: 100
  },
  {
    field: "联系电话",
    width: 50,
    input: null
  },
  {
    field: "焊接简历",
    title:"从事焊接工作简历",
    
    width: 70,
    input: null
  },
  {
    field: "WPS编号",
    title: "WPS/pWPS编号",
    input: null
  },
  {
    field: "新证",
    title: "新证/验证",
    width: 50
  },
  {
    field: "原证书编号",
    width: 60
  },
  {
    field: "产品类型",
    width: 60
  },
  {
    field: "定位焊",
    width: 50,
    input: null
  },
  {
    viewName: "combobox",
    field: "焊接方法2",
    title: "焊接方法",
    sortable: true,
    with: 30
  },
  {
    viewName: "combobox",
    field: "母材性质",
    title: "母材"
  },
  {
    viewName: "input",
    field: "填充金属",
    title: "填充金属类型",
    disabled: true,
    with: 30
  },
  {
    viewName: "combobox",
    field: "试件形式",
    sortable: true
  },

  {
    field: "板厚",
    title: "可焊板厚",
    sortable: true
  },
  {
    field: "管厚",
    title: "可焊管厚",
  },
  {
    viewName: "combobox",
    field: "管径",
    title: "可焊管径",
  },

  {
    viewName: "combobox",
    field: "接头形式",
    title: "焊接接头形式",
    width: 70
  },
  {
    field: "合格位置",
    title: "合格位置"
  },
  {
    field: "其他细节1",
    width: 50
  },
  {
    field: "其他细节2",
    width: 50
  }
];

//焊工总清单
var WeldTotalForm = [
  {
    field: "船级社证书号"
  },
  {
    viewName: "datebox",
    field: "发证日期"
  },
  {
    viewName: "datebox",
    field: "到期日期"
  },
  {
    field: "姓名",
    sortable: true,
    input: null
  },
  {
    field: "身份证",
    sortable: true,
    input: null
  },
  {
    viewName: "combobox",
    field: "性别",
    input: null,
    width: 50
  },
  {
    viewName: "combobox",
    field: "船级社",
    input: null,
    width: 50
  },
  {
    viewName: "combobox",
    field: "工区",
    title: "所属工区",
    input: null
  },
  {
    viewName: "combobox",
    field: "施工队",
    sortable: true,
    input: null
  },
  {
    viewName: "combobox",
    field: "焊接方法2",
    title: "焊接方法",
    sortable: true,
    input: null
  },
  {
    viewName: "combobox",
    field: "试件形式",
    sortable: true,
    input: null
  },
  {
    field: "合格位置",
    title: "合格位置",
    sortable: true,
    input: null
  },
  {
    field: "可焊位置",
    title: "可焊位置",
    sortable: true,
    input: null
  },
  {
    field: "板厚",
    title: "可焊板厚",
    sortable: true,
    input: null
  },
  {
    field: "管厚",
    title: "可焊管厚",
    input: null
  },
  {
    viewName: "combobox",
    field: "管径",
    title: "可焊管径",
    input: null
  },
  {
    viewName: "combobox",
    field: "母材性质",
    input: null,
    width: 50
  },
  {
    field: "填充金属",
    title: "填充金属类型",
    input: null
  },
  {
    viewName: "combobox",
    field: "接头形式",
    input: null
  },
  {
    field: "WPS编号",
    title: "WPS/pWPS编号",
    editor: {
      type: "textbox"
    }
  },
  
  {
    field: "PDF"
  },
  {
    viewName: "combobox",
    field: "在厂状态",
    title: "状态"
  }
];
