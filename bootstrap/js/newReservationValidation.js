function validateForm() {
		var x = document.getElementById("startTime").value;
		var temp = true;
		var z = document.getElementById("duration").value;
		var time = new Date(0,0,0, x.split(':')[0], x.split(':')[1], 00, 0);
		var correctTime=new Date(time.getTime() + z*60000).toString();
		var y=correctTime.split(':')[0].split(" ")[4]+":"+correctTime.split(':')[1]
		var rs = document.getElementById("resourceStartTime").value;
		var re = document.getElementById("resourceEndTime").value;
		if (x < rs) {
			alert("Sorry, Reservation start time entered is before resource start time. Reservation Unsuccessfull!")
			temp = false;
			return false;
		}
		
		if (y > re) {
			alert("Sorry, Reservation duration entered is after the resource end time. Reservation Unsuccessfull !")
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