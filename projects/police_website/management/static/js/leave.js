// DOM Elements

const leaveRestForm = document.getElementById("LeaveRequestForm"),
  firstName = document.getElementById("FirstName"),
  lastName = document.getElementById("LastName"),
  employeeID = document.getElementById("EmployeeID"),
  initialRemainingDays = document.getElementById("RemainingDays"),
  startDate = document.getElementById("StartDate"),
  endDate = document.getElementById("EndDate");

leaveRestForm.onsubmit = (e) => {
  e.preventDefault();
  (firstName.vale === "",
  lastName.value === "",
  employeeID.value === "",
  initialRemainingDays.value === "")
    ? alert("Complete all fields!")
    : createLeaveRequest();

  function createLeaveRequest() {
    let leaveRequest = document.createElement("div");

    leaveRequest.innerHTML = `
     <header class="text-center mb-5">
      <i
        class="bi bi-person-fill display-1 text-primary"
        style="font-size: 10rem"
      ></i>
      <h1 class="display-1 h1">Leave request form</h1>
    </header>
    <main class="container">
      <section class="row mb-3">
        <div class="col font-medium">
          <label for="">First Name:</label>
          <span class="text-primary">${firstName.value}</span>
        </div>
         <div class="col  ">
     <label class="text-lg ">Last Name:</label>
     <span class="text-primary" >${lastName.value}</span>
   </div>
      </section>
        <section class="row mb-3">
        <div class="col font-medium">
          <label for="">Employee ID:</label>
          <span class="text-primary">${employeeID.value}</span>
        </div>
         <div class="col  ">
     <label class="text-lg ">Initial leave days:</label>
     <span class="text-primary" >${initialRemainingDays.value}</span>
   </div>
      </section>
        </section>
        <section class="row mb-3">
        <div class="col font-medium">
          <label for="">Start Date:</label>
          <span class="text-primary">${startDate.value}</span>
        </div>
         <div class="col  leading-6 font-medium">
     <label class="text-lg ">End Date:</label>
     <span class="text-primary" >${endDate.value}</span>
   </div>
      </section>

        </section>
        <section class="row mb-3">
        <div class="col font-medium">
          <label for="">Requesting leave:</label>
          <span class="text-primary">${employeeID.value}</span>
        </div>
         <div class="col  ">
     <label class="text-lg ">Remaining leave day/s:</label>
     <span class="text-primary" >${initialRemainingDays.value}</span>
   </div>
      </section>

 <section class="mb-3 row">
   <div class="col   leading-6 font-medium">
     <label >Requesting leave:</label>
     <span class="text-indigo-700"
       >${calculateLeaveDays(startDate.value, endDate.value)} </span
     >
   </div>

   <div class="col   leading-6 font-medium">
     <label >Remaining leave day/s:</label>
     <span class="text-indigo-700"
       >${calculateRemainingLeaveDays(initialRemainingDays.value)}
       </span
     >
   </div>
 </section>
      <div class="col  ">
   <label >Submitted:</label>
   <span class="text-primary">${getSubmissionTimeStamp()} </span>
 </div>
 <!-- todo: buttons -->
 <section class="d-flex justify-content-between mt-3">
   <button type="submit" class="btn btn-success btn-lg " onclick="onLeaveApproval()"><i class="bi bi-emoji-smile-fill me-2 "></i>Approve</button>
   <button type="submit" class="btn btn-danger btn-lg" onclick="onLeaveReject()"><i class="bi bi-emoji-frown-fill me-2"></i>Decline</button>
 </section>
    </main>
    `;
    document.querySelector(".leave-request").remove();
    document.querySelector(".container").appendChild(leaveRequest);
  }
};
function getSubmissionTimeStamp() {
  this.today = new Date();

  const date = `${today.getFullYear()}-${
    today.getMonth() + 1
  }-${today.getDate()}`;
  const time = ` ${today.getHours()}:${today.getMinutes()}:${today.getSeconds()}`;
  const dateTime = `${date} / ${time}`;
  return dateTime;
}

// Calculate the exact leave days

function calculateLeaveDays(start, end) {
  const startDate = new Date(start);
  const endDate = new Date(end);

  let leaveDays = endDate.workingDaysFrom(startDate);
  return leaveDays;
}
// Calculate remaining leave days

function calculateRemainingLeaveDays(initialRemainingDays) {
  return (
    initialRemainingDays - calculateLeaveDays(startDate.value, endDate.value)
  );
}

Date.prototype.workingDaysFrom = function (fromDate) {
  if (!fromDate || isNaN(fromDate) || this < fromDate) {
    return -1;
  }

  let frDay = new Date(fromDate.getTime()),
    toDay = new Date(this.getTime()),
    numOfWorkingDays = 1;

  frDay.setHours(0, 0, 0, 0);
  toDay.setHours(0, 0, 0, 0);

  while (frDay < toDay) {
    frDay.setDate(frDay.getDate() + 1);
    let day = frDay.getDay();
    if (day != 0 && day != 6) {
      numOfWorkingDays++;
    }
  }
  console.log(numOfWorkingDays);
  return numOfWorkingDays;
};

// On Approve

function onLeaveApproval() {
  document.querySelector(".container").innerHTML = `
      <header class="text-center mb-5">
  <i class="bi bi-emoji-smile-fill h1 display-1 text-success m-auto"style="font-size: 10rem"></i>

  <h1 class="h1 display-1">Your leave was approved</h1>
  <button class="btn btn-dark  btn-lg mt-5" onclick="location.reload()">Back</button>
</header>
    `;
}
// On Reject
function onLeaveReject() {
  document.querySelector(".container").innerHTML = `
      <header class="text-center mb-5">
  <i class="bi bi-emoji-frown-fill h1 display-1 text-danger m-auto" style="font-size: 10rem"></i>

  <h1 class="h1 display-1">Your leave was declined</h1>
  <button class="btn btn-dark btn-lg mt-5" onclick="location.reload()">Back</button>

</header>
    `;
}