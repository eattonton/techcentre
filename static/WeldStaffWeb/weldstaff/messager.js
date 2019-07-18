(function(prop) {
  var $ = prop.$ || prop.JQuery;
  var messager = $.messager || {};
  messager.info = function(cellType, msg, timeout) {
    var parent = $("#msg_container");
    if (parent.length <= 0) {
      parent = $("<div id='msg_container' ></div>");
      $("body").append(parent);
    }
    parent.css({
      position: "absolute",
      zIndex: 10000,
      top: 0,
      right: 10,
      minWidth: 200
    });
    function remove(cell, timeout) {
      return function() {
        setTimeout(function() {
          cell.remove();
        }, timeout);
      };
    }

    function appendCell(cellType, msg, timeout) {
      var item = $(
        "<div class='msg_item' style='border-radius:8px;text-indent:5px;'></div>"
      );
      item.css({
        position: "relative",
        right: 0,
        marginTop: 8,
        padding: 5
      });
      if (cellType == "success") {
        item.css({
          background: "rgba(18, 19, 18, 0.4)",
          color: "#2cdc39"
        });
      }
      if (cellType == "error") {
        item.css({
          background: "rgba(18, 19, 18, 0.4)",
          color: "red"
        });
        timeout = timeout || 4000;
      }
      if (cellType == "warning") {
        item.css({
          background: "rgba(18, 19, 18, 0.4)",
          color: "yellow"
        });
        timeout = timeout || 3000;
      }
      item.text(msg);
      parent.append(item);
      remove(item, timeout)();
    }
    appendCell(cellType, msg, timeout || 2000);
  };
  $.messager = messager;
  $.Dialog = function(id, content, okCall, cacelCall, config) {
    var _config = $.extend(
      {
        title: "对话框",
        modal: true,
        cache: false,
        width: 400,
        height: 300,
        onClose: function() {
          $("#" + id).remove();
        }
      },
      config || {}
    );

    cacelCall =
      cacelCall ||
      function() {
        $("#" + id).dialog("close");
      };

    var buttons = [];
    okCall && buttons.push({ text: "确定", handler: okCall });
    cacelCall && buttons.push({ text: "关闭", handler: cacelCall });
    buttons = _config.buttons || buttons;
    _config.buttons = buttons;
    var div = $("<div id='{0}' style='padding:15px'></div>".format(id));
    div.css({  width: "100%", height: "100%" });
    $("body").append(div);
    div.append(content);
    $("#" + id).dialog(_config);
  };
})(window);
