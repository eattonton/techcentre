/**
 * Created by micometer on 2019/8/29.
 */
(function (prop) {
    if (!prop.layui) {
        return alert("请现在加载layui");
    }
    if (!prop.$) {
        return alert("请现在家中jquery");
    }

    var layuiplugins = prop.layuiplugins || {};
    var selected = {
        setSeleec: function (item) {

        },
        getSelects: function () {

        },
        unselectAll: function () {

        },
        selectAll: function () {

        },
    }
    var clicked = {
        onRowClick: function () {

        },
        onItemClick: function () {

        },
        onRightClick: function () {

        },
        onDbClick: function () {

        }
    }
    var update = {
        onBeforeUpdate: function (item) {

        },
        onAfterUpdate: function (item) {

        },
        updateItem: function (item) {
            if (this.onBeforeUpdate(item)) {

            }

            this.onAfterUpdate(item);
        },
    }
    var add = {
        onBeforeAdd: function (item) {

        },
        onAfterAdd: function (item) {

        },
        addItem: function (item) {
            if (this.onBeforeAdd(item)) {

            }

            this.onAfterAdd(item);
        }
    }
    var del = {
        onBeforeDelete: function (item) {
            return item;
        },
        onAfterDelete: function (item) {
        },
        deleteItem: function (item) {
            if (this.onBeforeDelete(item)) {

            }

            this.onAfterDelete(item);
        }
    }
    var edit = {
        onBeforeEdit: function (item) {
            return item;
        },
        onAfterEdit: function () {

        },
        editItem: function (item) {
            if (this.onBeforeEdit(item)) {

            }

            this.onAfterEdit(item);
        }
    }
    var data = {
        loadData: function (data) {
            if (this.onBeforeLoad(data)) {
                this.__data = data;
            }

            this.onAfterLoad(data);
        },
        loadFromUrl: function (url, parmas) {
            var that = this;
            $.ajax({
                url: url,
                data: JSON.stringify(parmas),
                success: function (data) {
                    that.loadData(data);
                },
                error: function (res) {
                    layer.msg("获取数据失败", "error");
                    console.log(msg);
                }
            })
        },
        onBeforeLoad: function (data) {
            return data;
        },
        onAfterLoad: function () {

        },
        lazyLoad: function () {

        }
    }

    var getItem = {
        getItemById: function (id) {
            return this.__data.find(function (cell) {
                return cell[this.rowId] == id;
            })
        },
        getItemByIndex: function (index) {
            return this.__data.length <= index && index >= 0 ? this.__data[index] : null;
        }
        getItemIndexById: function (itemId) {
            var index = -1;
            this._data.find(function (cell, _idx) {
                if (cell[this.rowId] == itemId) {
                    index = _idx;
                }
                return index == _idx;
            });
            return index;
        }
        ,
        filterItem: function (callack) {
            return this.__data.filter(callack);
        }
        ,
        updateRowStyle: function (id, style) {

        }
        ,
        updateCellStyle: function (id, colname, style) {

        }
        ,
        updateHeader: function (columns) {
            this.default.columns = columns;
        }
        ,
    }

    function table(config) {
        var methods = {};
        $.extend(methods, getItem, data, edit, del, add, update, clicked, selected);

        var defaultF = {
            rowId: "id",
            __data: [],
        };

        /**开始渲染**/
        function render(config) {
            $.extend(defaultF, config || {});
            if (!defaultF.id) {
                return layer.msg("请输入表格Id");
            }
            var table = layui.table;
            table.render(defaultF);
        }

        function resize() {

        }

        $.extend((this.default, config));
    }

    layuiplugins.table = function (config) {
        return new table(config || {});
    };
    prop.layuiplugins = layuiplugins;
})(window)