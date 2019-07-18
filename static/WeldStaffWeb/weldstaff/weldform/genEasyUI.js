/**
 * 基于easyui的方法
 * 根据用户的配置生成相关的表单数据
 * 配置类型如下格式
 * {
 *  viewName:"easyui对应的类型"
 * }
 */
(function (prop) {
    var _ = prop._ || {};

    var genEasyUi = prop.genEasyUi || {};
    var $ = prop.$ || prop.JQuery;

    function cloneDeep(cell) {
        if (cell instanceof Array) {
            return cell.map(cloneDeep);
        } else {
            var obj = {};
            for (var key in cell) {
                var value = cell[key];
                if (value instanceof Array) {
                    obj[key] = cloneDeep(value);
                } else if (value instanceof Function) {
                    obj[key] = value;
                } else if (value instanceof Object) {
                    obj[key] = cloneDeep(value);
                } else {
                    obj[key] = value;
                }
            }
            return obj;
        }
    }

    //对一维度的配置元素进行深拷贝
    _.cloneDeep = function (value) {
        return cloneDeep(value);
    };

    /**
     * 不同类型对应的基础元素类型
     */
    var targetTypeMap = {
        textbox: "input",
        passwordbox: "input",
        filebox: "input",
        combo: "input",
        checkbox: "input",
        radio: "input",
        combobox: "input"
    };

    /**
     * 获取easyui对应的方法
     */
    var gen = {
        base: function (config) {
            if (!config || !config.id) {
                console.log("请明确元素的ID");
                return false;
            }
            return true;
        },
        getId: function (config) {
            if (config.id.indexOf("#") == 0) {
                return config.id;
            }
            return "#" + config.id;
        },
        getItem: function (config) {
            var id = gen.getId(config);
            var item = $(id);
            if (item.length <= 0) {
                console.log(id);
            }
            return item;
        },
        datebox: function (config) {
            gen.base(config) && gen.getItem(config).datebox(config);
        },
        textbox: function (config) {
            gen.base(config) && gen.getItem(config).textbox(config);
        },
        passwordbox: function (config) {
            gen.base(config) && gen.getItem(config).passwordbox(config);
        },
        filebox: function (config) {
            gen.base(config) && gen.getItem(config).filebox(config);
        },
        checkbox: function (config) {
            gen.base(config) && gen.getItem(config).iCheckbox(config);
        },
        combobox: function (config) {
            gen.base(config) && gen.getItem(config).combobox(config);
        },
        radio: function (config) {
            gen.base(config) && gen.getItem(config).iRadiobutton(config);
        },
        combo: function (config) {
            gen.base(config) && gen.getItem(config).combo(config);
        }
    };
    genEasyUi.getElement = function (config) {
        var call = gen[config.viewName];
        if (_.isUndefined(call)) {
            call = config.render;
        }
        if (_.isUndefined(call)) {
            console.log("不支持的类型", config);
            return;
        }
        return call;
    };

    genEasyUi.getForm = function (form, elements, rowFunc) {
        elements = _.cloneDeep(elements);
        if (!form || !form.id) {
            console.log("请明确表单所属的元素ID");
            return {};
        }
        var colCount = parseInt(form.colCount || 1);
        var id = form.id;
        if (id.indexOf("#") === 0) {
            id = id.replace("#", "");
        }

        /**
         * 为元素添加id号
         */
        var genElement = elements.filter(function (cell) {
            cell.id = cell.id || id + (cell.name || cell.field || cell.title);
            cell.label = cell.title;
            return cell.input !== null;
        });

        var rows = Math.ceil(genElement.length / colCount);
        rowFunc =
            rowFunc ||
            function () {
                return $("<div class='dialog-row'></div>");
            };
        var _genElement = _.cloneDeep(genElement);

        function renderOne(cells) {
            var parent = rowFunc();
            cells.map(function(cell) {
                var target = targetTypeMap[cell.viewName] || "div";
            var name = cell.name || cell.field || cell.title;
            var element = "<{0} id={1} name={2}></{0}>";
            var ele = $(element.format(target, cell.id, name));
            parent.append(ele);
        })
            ;
            return parent;
        }

        for (index = 0; index < rows; index++) {
            $("#" + id).append(renderOne(_genElement.splice(0, colCount)));
        }

        /**
         * 获取需要调用的easyui对应的方法
         * @param {元素} cell
         */
        var getCall = function (cell) {
            var item = $("#" + cell.id);
            var call = item[cell.viewName];
            return call;
        };

        /**
         * 获取输入框数据
         * @param {表单中元素} elements
         */
        var getFormValues = function (elements) {
            return function (onlyValue) {
                onlyValue = onlyValue || false;
                var values = {};
                elements.map(function(cell){
                    var call = getCall(cell);
                if (call) {
                    var value = call.call($("#" + cell.id), "getValue");
                    if (onlyValue && _.isEmpty(value)) {
                        return;
                    }
                    values[cell.name || cell.field] = value;
                }
            })
                ;
                return values;
            };
        };
        /**
         * 设置输入框数据
         * @param {} elements
         */
        var setFormValues = function (elements) {
            return function (values) {
                elements.map(function(cell){
                    var call = getCall(cell);
                call &&
                call.call(
                    $("#" + cell.id),
                    "setValue",
                    values[cell.name || cell.field]
                );
            })
                ;
            };
        };

        /**
         * 清空输入框数据
         */
        var resetFieldValues = function () {
            return function (values) {
                elements.map(function(cell){
                    var call = getCall(cell);
                call &&
                call.call(
                    $("#" + cell.id),
                    "setValue",
                    values ? values[cell.name || cell.field] : ""
                );
            })
                ;
            };
        };

        var showFields = function () {
            /**
             * 显示或隐藏字段
             */
            return function (values) {
                elements.map(function(cell){
                    var item = $("#" + cell.id);
                var itemParent = item.parent();
                if (!!values[cell.name || cell.field]) {
                    itemParent.css({display: "none"});
                } else {
                    itemParent.css({display: "block"});
                }
            })
                ;
            };
        };

        /**
         * 向元素中追加获取数据和设置数据的方法
         */
        $("#" + id).data("getValues", getFormValues(genElement));
        $("#" + id).data("setValues", setFormValues(genElement));
        $("#" + id).data("resetValues", resetFieldValues(genElement));
        $("#" + id).data("showFields", showFields(genElement));
        return genElement;
    };

    var dataGrid = function (id) {
        var obj = {
            getSelect: function () {
                return $("#" + id).datagrid("getSelected");
            },
            getSelects: function () {
                return $("#" + id).datagrid("getSelections");
            },
            getChecked: function () {
                return $("#" + id).datagrid("getChecked");
            },
            getData: function () {
                return $("#" + id).datagrid("getData");
            },
            getItemById: function (id) {
                return obj.getItemByIndex(obj.getIndexByItemId(id));
            },
            getItemByIndex: function (index) {
                var data = obj.getData();
                if (data.length > 0) return data[index];
                console.log("不存在有效的数据行");
                return null;
            },
            getIndexByItemId: function (itemOrItemId) {
                var id = itemOrItemId;
                if (_.isObject(id)) {
                    id = id.id || id._id;
                }
                return $("#" + id).datagrid("getRowIndex", id);
            },
            selectRow: function (rowOrIndex) {
                var index = obj.getIndexByItemId(rowOrIndex);
                return $("#" + id).datagrid("selectRow", index);
            },
            updateRow: function (row) {
                var index = obj.getIndexByItemId(row);
                if (typeof index == undefined) {
                    return console.log("获取数据行失败");
                }
                $("#" + id).datagrid("updateRow", {
                    index: index,
                    row: {data: row}
                });
            },
            appendRow: function (row) {
                $("#" + id).datagrid("appendRow", row);
            },
            insertRow: function (row, index) {
                index = index || -1;
                $("#" + id).datagrid("appendRow", {index: index, row: row});
            },
            deleteById: function (rowOrRowId) {
                var index = obj.getIndexByItemId(rowOrRowId);
                if (typeof index == undefined) {
                    return console.log("获取索引失败");
                }
                $("#" + id).datagrid("deleteRow", index);
            },
            showColumn: function (field) {
                $("#" + id).datagrid("showColumn", field);
            },
            hideColumn: function (field) {
                $("#" + id).datagrid("hideColumn", field);
            }
        };
    };
    prop.genEasyUi = genEasyUi;
    prop.dataGrid = dataGrid;
    prop.DataGridExtend = {
        getSelectionsByRowNumber: function (datagridId, start, end) {
            var start = parseInt(start);
            var end = parseInt(end);
            if (!isNaN(start) && !isNaN(end)) {
                var datas = $('#' + datagridId).datagrid('getData');
                return datas.rows.filter(function (cell, index) {
                    return index >= start - 1 && index <= end - 1;
                })
            }
            return $('#' + datagridId).datagrid('getSelections');
        }
    }
})(window);
