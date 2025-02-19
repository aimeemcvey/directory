$(document).ready(function(){
    $('.header').height($(window).height());
  })

// Default open first tab
document.getElementById("defaultOpen").click();

function openTab(evt, tabName) {
  // Declare all variables
  var i, tabcontent, tablinks;
  
  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  
  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("nav-link");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  
  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";

  var t = {'table': tabName};
  // alert(t)
  
  $.ajax({
    type: "POST",
    url:"/table_choice",
    data: t,
    dataType: 'json',
  });
}

// Grays out Choose Report option
$("#choice").change(function () {
  if($(this).val() == "0") $(this).addClass("empty");
  else $(this).removeClass("empty")
});

$("#choice").change();