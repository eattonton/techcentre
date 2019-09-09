/**
 * Created by micometer on 2019/8/27.
 */

(function (prop) {
    if (!prop.layui) {
        return alert("请现在加载layui");
    }
    if (!prop.$) {
        return alert("请现在家中jquery");
    }

    var layuiplugins = prop.layuiplugins || {};

    var sidemune = {
        default: {
            type: "horizon",
            onItemClick: null,
            onAfterRender: null,
            onAfterUpdate: null,
            onAfterHide: null,
            data: [],
            container: "",
        },
        //设置导航栏的宽度
        changeModal: function (isSnap) {
            if (isSnap) {
                $("#" + this.default.container).find("cite,.layui-nav-more").css("display", "none");

            } else {
                $("#" + this.default.container).find("cite,.layui-nav-more").css("display", "inline-block");
            }
            return sidemune;
        },
        //渲染数据
        render: function () {
            var container = sidemune.default.container;
            if (!container) {
                layer.msg("请输入container");
            }
            container = $("#" + container);
            container.empty();

            function apendItem(item, parent, index) {
                var li = $("<li class='layui-nav-item layui-nav-itemed'></li>");
                var al = $("<a href='javascript:;'></a>");
                if (item.icon) {
                    al.append("<i class='layui-icon layui-icon-" + item.icon + "'></i>");
                }
                al.append("<cite>" + item.label + "</cite>");
                al.attr("id", item.id);
                var target = li;
                if (index == 1) {
                    al.appendTo(li);
                    li.appendTo(parent);
                } else {
                    var dl = $('<dl class="layui-nav-child"></dl>');
                    var dd = $("<dd></dd>");
                    dl.appendTo(parent);
                    dd.appendTo(dl);
                    al.appendTo(dd);
                    dd.css("paddingLeft", index * 5);
                    target = dd;
                    if (!item.children) {
                        dd.addClass("sidemenu");
                    }
                }
                target.data("path", (parent.data("path") || "") + "/" + target.text());
                (item.children || []).forEach(function (cell) {
                    apendItem(cell, target, index + 1);
                });
            }

            function appendSideMenu() {
                var ul = $("<ul class='sidemune' style='width: 100%'></ul>").addClass("layui-nav layui-nav-tree layui-inline");
                return ul;
            }

            var ul = appendSideMenu();
            sidemune.default.data.forEach(function (cell) {
                apendItem(cell, ul, 1);
            });
            ul.appendTo(container);
            container.find(".sidemenu").click(sidemune.default.onItemClick);
            sidemune.default.onAfterRender && sidemune.default.onAfterRender(sidemune);
            return sidemune;
        },
        //更新数据行数据
        updateItem: function (item) {
            var itemId = item.id;
            var old = $("#" + itemId);
            var icon = old.find(".layui-icon");
            var _class = icon.attr("class").split(" ");
            var info = _class.filter(function (cell) {
                return cell.trim().indexOf("layui-icon") == -1;
            });
            info.push("layui-icon");
            if (item.icon) {
                info.push("layui-icon-" + item.icon);
                icon.attr("class", info.join(" "));
            }
            old.find("cite").text(item.label);
            sidemune.default.onAfterUpdate && sidemune.default.onAfterUpdate(itemId);
            return sidemune;
        },
        //隐藏按钮
        hideItem: function (itemId) {
            $("#" + itemId).hide();
            sidemune.default.onAfterHide && sidemune.default.onAfterHide(itemId);
            return sidemune;
        },
        //系统初始化
        init: function (options) {
            sidemune.default = $.extend(true, sidemune.default, options || {});
            return sidemune;
        }
    };
    layuiplugins.sidemenu = function (config) {
        return sidemune.init(config || {});
    };
    prop.layuiplugins = layuiplugins;
})(window);
