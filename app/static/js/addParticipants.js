$(document).ready(function(){
  $(".Volunteers").hide();
  $("#Volsearch").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#Volul a").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
      if(!value) {
        $(".Volunteers").hide();
      }
    });
  });
});

function addVolunteer(e){
  volunteersName = $(e).text()
  $("#Volunteertable").append('<tr><td>' + volunteersName + '</td><td><button id="removeButton" onclick="removeVolunteer(this)" type="button">x</button></td></tr>')
  console.log(volunteersName)

}
function removeParticipants(e) {
  text = $(e).parent().parent()[0].textContent;
  $(e).parent().parent().remove();
}

function removeVolunteer(e) {
  $(e).parent().parent().remove();
}
count = 0;
function addOutsideParticipant() {
  console.log("Function called");
  opList = ["email", "firstName", "lastName", "phoneNumber"];
  opList.forEach(item => {
    $("<input type='text'/>")
   .attr("value", $('#'+item+'Textarea').val())
   .attr("id", item+count)
   .attr("name", item+count)
   .appendTo("#OutsideTable")
  }
)
count++;
}


// function textboxValue() {
//   var formValues = {
//       event: "2",
//       firstName: $("#firstNameTextarea").val(),
//       lastName: $("#lastNameTextarea").val(),
//       emailEntry: $("#emailTextarea").val(),
//       phoneNumber: $("#phoneNumberTextarea").val(),
//     };
//   var formStringified = JSON.stringify(formValues, null, 2);
//   $.ajax({
//     method: "POST",
//     url: "/createParticipant",
//     data: formStringified,
//     contentType: "application/json; charset=utf-8",
//     success: function(response) {
//       console.log("Success");
//     },
//     error: function(request, status, error) {
//       console.log(status,error);
//     }
//   });
// };
