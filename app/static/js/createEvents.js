// updates max and min dates of the datepickers as the other datepicker changes
function updateDate(obj) {
  // we need to replace "-" with "/" because firefox cannot turn a date with "-" to a datetime object
  var selectedDate = ($(obj).val()).replaceAll("-", "/")
  var dateToChange = new Date(selectedDate);
  var newMonth = dateToChange.getMonth();
  var newYear = dateToChange.getFullYear();
  var newDay = dateToChange.getDate();
  if(obj.id == "startDatePicker") {
    $("#endDatePicker").datepicker({minDate: new Date(  newYear, newMonth, newDay)});
    $("#endDatePicker").datepicker( "option", "minDate", new Date(  newYear, newMonth, newDay));
  }

  if (obj.id == "endDatePicker") {
    $("#startDatePicker").datepicker({maxDate: new Date(  newYear, newMonth, newDay)});
    $("#startDatePicker").datepicker("option", "maxDate", new Date(  newYear, newMonth, newDay));
  }
}
// turns a string with a time with HH:mm format to %I:%M %p format
// used to display 12 hour format but still use 24 hour format in the backend
function format24to12HourTime(timeStr){
  var formattedTime;
    if (parseInt(timeStr.slice(0, 2)) > 12){
      formattedTime = "0" + String(parseInt(timeStr.slice(0, 2)) - 12) + timeStr.slice(2) + " PM";
    }
    else if (parseInt(timeStr.slice(0, 2)) < 12 ){
      formattedTime =  timeStr + " AM";
    }
    else {
      formattedTime = timeStr + " PM";
    }
    return formattedTime;
  }
/*
 * Run when the webpage is ready for javascript
 */
$(document).ready(function() {
    $("#attachmentObject").fileinput({
        overwriteInitial: "false",
    });
  $("#checkIsRecurring").click(function() {
    var recurringStatus = $("input[name='isRecurring']:checked").val()
    if (recurringStatus == 'on') {
      $("#endDateStyle, #recurringTableDiv").removeClass('d-none')
      $("#endDatePicker").prop('required', true);
    } else {
      $("#endDateStyle, #recurringTableDiv").addClass('d-none')
      $("#endDatePicker").prop('required', false);
    }
  });
  // everything except Chrome
  if (navigator.userAgent.indexOf("Chrome") == -1) {
    $('input.timepicker').timepicker({
             timeFormat : 'hh:mm p',
             scrollbar: true,
             dropdown: true,
             dynamic: true,
             minTime: "08:00am",
             maxTime: "10:00pm"
    });
    $(".timepicker").prop("type", "text");
    $(".timeIcons").prop("hidden", false);

    var formattedStartTime = format24to12HourTime($("#startTime").prop("defaultValue"));
    var formattedEndTime = format24to12HourTime($("#endTime").prop("defaultValue"));
    $("#startTime").val(formattedStartTime);
    $("#endTime").val(formattedEndTime);
  }
  else {
    $(".timepicker").prop("type", "time");
    $(".timeIcons").prop("hidden", true);
  }

  if ($(".datePicker").is("readonly")) {
    $( ".datePicker" ).datepicker( "option", "disabled", true )
  };

  //makes the input fields act like readonly (readonly doesn't work with required)
  $(".readonly").on('keydown paste', function(e){
        if(e.keyCode != 9) // ignore tab
            e.preventDefault();
  });

  $.datepicker.setDefaults({
    minDate:  new Date($.now()),
    dateFormat:'mm-dd-yy'
  });

  $("#startDate").click(function() {
    $("#startDatePicker").datepicker().datepicker("show");
  });

  $("#endDate").click(function() {
    $("#endDatePicker").datepicker().datepicker("show");
  });


  $("#startDatePicker, #endDatePicker").change(function(){
    if ( $("#startDatePicker").val() && $("#endDatePicker").val()){
      var eventDatesAndName = {name:$("#inputEventName").val(),
                               isRecurring: true,
                               startDate:$("#startDatePicker").val(),
                               endDate:$("#endDatePicker").val()}
      $.ajax({
        type:"POST",
        url: "/makeRecurringEvents",
        data: eventDatesAndName, //get the startDate, endDate and name as a dictionary
        success: function(jsonData){
          var recurringEvents = JSON.parse(jsonData)
          var recurringTable = $("#recurringEventsTable")
          $("#recurringEventsTable tbody tr").remove();

          for (var event of recurringEvents){
            eventdate= new Date(event.date).toLocaleDateString()
            recurringTable.append("<tr><td>"+event.name+"</td><td><input name='week"+event.week+"' type='hidden' value='"+eventdate+"'>"+eventdate+"</td></tr>");
            }
        },
        error: function(error){
          console.log(error)
        }
      });
    }
  });

  $("#checkIsTraining").click(function(){
    if ($("input[name='isTraining']:checked").val() == 'on'){
      $("#checkIsRequired").prop('checked', true);

    } else{
      $("#checkIsRequired").prop('disabled', false);
    }
  });
});
