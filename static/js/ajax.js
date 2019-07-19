var err = function(res) {
  console.log(res);
};
var isDebug = false;

function ajaxLoading() {
  $('<div class="datagrid-mask"></div>')
    .css({ display: "block", width: "100%", height: $(window).height() })
    .appendTo("body");
  $('<div class="datagrid-mask-msg" style="height:22px"></div>')
    .html("正在处理，请稍候。。。")
    .appendTo("body")
    .css({
      display: "block",
      left: ($(document.body).outerWidth(true) - 190) / 2,
      top: ($(window).height() - 45) / 2
    });
}
function ajaxLoadEnd() {
  $(".datagrid-mask").remove();
  $(".datagrid-mask-msg").remove();
}

var AJAX = {
  base: function(url, success, config) {
    if (isDebug) return success({ state: true, data: param });
    var _config = $.extend({}, config || {});
    _config.success = function(res){
      try{
        success && success(res)
      }catch(e){
        console.log(e);
      }
    };
    _config.error = _config.error || err;
    _config.url = url;
    _config.beforeSend = ajaxLoading;
    _config.complete = ajaxLoadEnd;
    return _config;
  },

  post: function(url, param, success, config) {
    var _config = AJAX.base(url, success, config);
    if (!_config) return;
    _config.data = { data: JSON.stringify(param || {}) };
    _config.type = "POST";
    $.ajax(_config);
  },
  get: function(url, param, success, config) {
    url = url + "?data=" + JSON.stringify(param || {});
    var _config = AJAX.base(url, success, config);
    if (!_config) return;

    _config.type = "get";
    $.ajax(_config);
  },
  postFile: function(url, param, success, config) {
    var _config = AJAX.base(url, success, config);
    if (!_config) return;
    var formData = new FormData();
    for (var key in param) {
      formData.append(key, param[key]);
    }
    _config.data = formData;
    _config.type = "POST";
    _config.contentType=false;
    _config.processData = false;
    $.ajax(_config);
  }
};
