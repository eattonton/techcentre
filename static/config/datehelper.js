var DateHelper = {}
 
//计算 某天开始的一周
DateHelper.GetOneWeek=function(nowDate){
    var res = []
    var weekday = []
    weekday[0] = "星期日"
    weekday[1] = "星期一"
    weekday[2] = "星期二"
    weekday[3] = "星期三"
    weekday[4] = "星期四"
    weekday[5] = "星期五"
    weekday[6] = "星期六"
 
    //移到星期一
    nowDate = DateHelper.GetCurMonday(nowDate)
    //var oneDay = nowDate.getDay()
    for(var i=1;i<=7;i++){
        res.push({"1":weekday[nowDate.getDay()],"2":nowDate.Format("M月d"),"3":nowDate.Format("Y-MM-dd")}) 
        nowDate.setDate(nowDate.getDate() +1)
    }

    return res
}

DateHelper.GetOneWeekStr=function(nowDate){
    var res = []
    //移到星期一
    nowDate = DateHelper.GetCurMonday(nowDate)
    var str1 = nowDate.Format("Y-MM-dd")
    //计算礼拜天
    var date2 = new Date(str1)
    date2.setDate(date2.getDate()+6)
    var str2 = date2.Format("Y-MM-dd")

    return str1+"_"+str2
}

//获得当前日期的星期一
DateHelper.GetCurMonday = function(nowDate){
    if(nowDate.getDay() == 0){
        //表示星期天
        nowDate.setDate(nowDate.getDate() - 6)
    }else{
        nowDate.setDate(nowDate.getDate() - nowDate.getDay() +1)
    }
    
    return nowDate
}
//获得上一个星期一
DateHelper.GetPrevMonday = function(nowDate){
    //移到星期一
    nowDate = DateHelper.GetCurMonday(nowDate)
    nowDate.setDate(nowDate.getDate() -7)
    return nowDate
}
//根据当前日期 获得下个星期的 日期列表
DateHelper.GetNextMonday =function(nowDate){
     //移到星期一
    nowDate = DateHelper.GetCurMonday(nowDate)
    nowDate.setDate(nowDate.getDate() +7)
    return nowDate
}

DateHelper.GetDateList = function(startDate, endDate){
    let arr1 = []
    let date1 = new Date(startDate["year"]+"-"+startDate["month"]+"-"+startDate["date"])
    let date2 = new Date(endDate["year"]+"-"+endDate["month"]+"-"+endDate["date"])

    let numDay = date2.getDate() - date1.getDate()+1
    console.log(numDay)
    for(let i=0; i<numDay;i++){
        let str1 = date1.Format("Y-MM-dd")
        let str2 = date1.Format("MM-dd")
        let str3 = date1.Format("dd")
        arr1.push({"1":str1,"2":str2,"3":str3})
        date1.setDate(date1.getDate() +1)
    }

    return arr1
}

 
