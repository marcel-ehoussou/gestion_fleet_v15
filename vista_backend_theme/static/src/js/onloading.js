//$(document).ready(function () {
//    console.log("Nous sommes dans le onloading");
//    $(".o_action_manager").addClass("sidebar_margin");
//    console.log($("ul.sidebar_menu:first-child"));
//    $("ul.sidebar_menu:first-child").addClass("active");
//});


$(document).ready(checkContainer);

function checkContainer () {
  if ($('ul.sidebar_menu').is(':visible')) { //if the container is visible on the page
    var active_menu_href = localStorage.getItem("active_menu");
    var active_menu = $("a.nav-link[href='" + active_menu_href + "']");
    if (active_menu) {
        active_menu.addClass("active");
    }else {
        $("ul.sidebar_menu li:first a.nav-link").addClass("active");
    }
  } else {
    setTimeout(checkContainer, 50); //wait 50 ms, then try again
  }


  $(document).on("click", ".nav-link", function(event){
    $('.nav-link').removeClass("active");
    $(this).addClass("active");
    localStorage.setItem("active_menu", $(this).attr('href'));
  });
}