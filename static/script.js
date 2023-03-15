    function myFunction() {
      document.getElementById("myDropdown").classList.toggle("show");
    }

    window.onclick = function() {
      if (!e.target.matches('.dropbtn')) {
      var myDropdown = document.getElementById("myDropdown");
        if (myDropdown.classList.contains('show')) {
          myDropdown.classList.remove('show');
        }
      }
    }


const dropdown = document.getElementById('Quizzes');
const button = document.getElementById('name');

button.addEventListener('click', () => {
  const selectedName = dropdown.value;
  button.textContent = selectedName;
});


var body = document.getElementsByTagName('body')[0];
body.style.height = body.scrollHeight + 'px';

