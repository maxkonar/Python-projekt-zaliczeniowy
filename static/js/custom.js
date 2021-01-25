function myFunction() {
  var x = document.getElementById("myLinks");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}

jQuery( document ).ready(function($){
    if($('label[for=username]').length){
        $('label[for=username]').text('Nazwa użytkownika');
    }
    if($('label[for=email]').length){
        $('label[for=email]').text('Adres Email');
    }
    if($('label[for=password]').length){
        $('label[for=password]').text('Hasło');
    }
    if($('.flashes li').text() == "Please log in to access this page."){
        $('.flashes li').text("Żeby mieć dostęp do panalu użytkownika należy się zalogować");
    }

});