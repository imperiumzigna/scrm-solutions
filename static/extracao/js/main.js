function move() {
	  var elem = document.getElementById("myBar");   
	  var width = 0;
	  var id = setInterval(frame, 120);
	  function frame() {
	    if (width >= 100) {
	      clearInterval(id);
	    } else {
	      width++; 
	      elem.style.width = width + '%'; 
	      document.getElementById("label").innerHTML = width * 1  + 'posts';
	    }
	  }
	}


