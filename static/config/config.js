var config = {}
//config.host="http://localhost/wx"
config.host = "http://172.50.51.217:8000"
config.domain = config.host
config.datatype = 'jsonp'
config.version="V1.0"
config.storageName="tcuser"
//get params
config.getQueryStringByName = function (name) {
    var result = location.search.match(new RegExp("[\?\&]" + name + "=([^\&]+)", "i"));
    if (result == null || result.length < 1) {
        return "";
    }
    return decodeURI(result[1]);
}
//自定义localstorage的过期逻辑
config.localParamSet = function (key, val) {
    var curTime = new Date().getTime();
    localStorage.setItem(key, JSON.stringify({data: val, time: curTime}))
}
config.localParamGet = function (key, exp) {
    var data = localStorage.getItem(key);
    if (data) {
        var dataObj = JSON.parse(data);
        return dataObj.data;
    } else {
        return null;
    }
}
//删除此记录
config.delQualityUser = function () {
    localStorage.removeItem(config.storageName);
}
//用户有效性检查
config.userValid = function (name, password, cb) {
    var user = {'name': name, 'pass': password};
    config.ajaxGet("/tc/user/find", {data: JSON.stringify(user)}, function (res) {
        typeof cb == 'function' && cb(res)
    }, {
        error: function (err) {
            config.alert("登陆失败")
        }
    });
}

//当前用户检测
config.userCheck = function (cb) {
    var userObj = config.localParamGet(config.storageName);
    if (userObj == null) {
        //无登陆信息
        location.href = './userlogin.html'
    } else {
        config.userValid(userObj.英文名, userObj.密码 || '', function (res) {
            if (res.data == 0) {
                location.href = './userlogin.html'
            }
        })
        typeof cb == 'function' && cb(userObj)
    }
}
//获得时间差，以天为单位
config.getDaySpan = function (dayStr1) {
    var day1 = new Date(dayStr1);
    var day2 = new Date();
    var day3 = day2 - day1;
    var MinMilli = 1000 * 60;  //1分钟
    var HrMilli = MinMilli * 60;  //小时
    var DyMilli = HrMilli * 24;  //天

    return Math.round(day3 / DyMilli);
}

config.myformatter = function (date) {
    var y = date.getFullYear();
    var m = date.getMonth() + 1;
    var d = date.getDate();
    return y + '-' + (m < 10 ? ('0' + m) : m) + '-' + (d < 10 ? ('0' + d) : d);
}
config.myparser = function (s) {
    if (!s) return new Date();
    var ss = (s.split('-'));
    var y = parseInt(ss[0], 10);
    var m = parseInt(ss[1], 10);
    var d = parseInt(ss[2], 10);
    if (!isNaN(y) && !isNaN(m) && !isNaN(d)) {
        return new Date(y, m - 1, d);
    } else {
        return new Date();
    }
}

config.ConfigParam = null;
//加载初始化文件
config.loadConfigParam = function(cb) {
        if (config.ConfigParam) {
            typeof cb == 'function' && cb(config.ConfigParam)
        } else {
            //加载配置
            $.getJSON("../tc/diction/get", function (data) {
                if (config.ConfigParam == null) {
                    config.ConfigParam = {}
                }
                $.extend(config.ConfigParam, data);
                typeof cb == 'function' && cb(config.ConfigParam)
            })
        }
    }

String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp("({" + key + "})", "g");
                    result = result.replace(reg, args[key]);
                }
            }
        }
        else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    //var reg = new RegExp("({[" + i + "]})", "g");//这个在索引大于9时会有问题，谢谢何以笙箫的指出
                    reg = new RegExp("({)" + i + "(})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
}

Date.prototype.Format = function (fmt) { //author: meizz   
    var o = {
        "Y+": this.getFullYear(), 
        "M+": this.getMonth() + 1, //月份   
        "d+": this.getDate(), //日   
        "H+": this.getHours(), //小时   
        "m+": this.getMinutes(), //分   
        "s+": this.getSeconds(), //秒   
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度   
        "S": this.getMilliseconds() //毫秒   
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}

config.alert = function (msg) {
    $.messager.alert("提示", msg);
}

config.confirm = function (msg, okcallback) {
    $.messager.confirm("提示", msg, function (r) {
        if (r) {
            return okcallback();
        }
    });
}
config.show = function (msg, title) {
    $.messager.show({
        title: title ? title : "提示",
        msg: msg,
        timeout: 1500,
        showType: 'slide',
    });

}

/*
 url:请求的地址,
 data:请求的数据,
 success:成功后的处理函数,
 method:请求方式，
 config:其他配置
 */
_ajax = function (url, data, success, method, config) {
    var _config = {
        url: url,
        data: data,
        type: method,
        success: success,
        error: function () {
            console.log("******操作失败*****");
            console.log({url: url, data: data});
        }
    };

    if (config) {
        $.extend(true, _config, config);
    }

    $.ajax(_config);
}

config.ajaxPost = function (url, data, success, config) {
    _ajax(url, data, success, "POST", config);
}

config.ajaxGet = function (url, data, success, config) {
    _ajax(url, data, success, "GET", config);
}

config.randomNum = function(minNum,maxNum){ 
    switch(arguments.length){ 
        case 1: 
            return parseInt(Math.random()*minNum+1,10); 
        break; 
        case 2: 
            return parseInt(Math.random()*(maxNum-minNum+1)+minNum,10); 
        break; 
            default: 
                return 0; 
            break; 
    } 
} 

//sparam对象 cb处理函数
config.doOnWeb = function(surl, sparam, cb, stype){
    var stype = stype || 'GET';
    $.ajax({
        url: surl,
        async: false,
        type: stype,
        data: sparam,
        success: function(res, status) {
            typeof cb == 'function' && cb(res)
        },
        //调用出错执行的函数
        error: function() {
            //请求出错处理
            alert("出错")
        }
    })
}

 