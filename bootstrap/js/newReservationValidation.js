function validateForm() {
		var x = document.getElementById("startTime").value;
		var temp = true;
		var y = document.getElementById("endTime").value;
		var z;
		var rs = document.getElementById("resourceStartTime").value;
		var re = document.getElementById("resourceEndTime").value;
		if (x < rs) {
			alert("Sorry, Reservation start time entered is before resource start time. Reservation Unsuccessfull!")
			temp = false;
			return false;
		}
		
		if (y > re) {
			alert("Sorry, Reservation end time entered is after the resource end time. Reservation Unsuccessfull !")
			temp = false;
			return false;
		}
		
		if (x > y) {
			alert(" Reservation end time cant be less than start time");
			temp = false;
			return false;
		}
		if (temp) {
			alert(" Success! Reservation Completed! ");
		}
}