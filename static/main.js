// For Profile Page
//====================================================================//
//Edit Button for Profile_Pic
const button = document.querySelector('#edit-btn');
button.addEventListener('click', () => {
    const url_form = document.querySelector('.image_url_hidden');
    const username = document.querySelector('.username');
    username.style.margin = '-20px';
    username.style.padding = '0';
    url_form.style.display = 'flex';
});

//Edit Button for Profile_Pic
const button1 = document.querySelector('#profile-cancel-btn');
button1.addEventListener('click', () => {
    const url_form = document.querySelector('.image_url_hidden');
    const username = document.querySelector('.username');
    username.style.margin = '20px';
    username.style.padding = '0';
    url_form.style.display = 'none';
});

//Edit Button for Name
const Name = document.querySelector('#name-btn');
Name.addEventListener('click', () => {
    const usersname = document.querySelector('#name');
    const input_box = document.querySelector('.nickname input');
    const save = document.querySelector('#save-btn');
    const cancel = document.querySelector('#cancel-btn');
    save.style.display = 'block';
    cancel.style.display = 'block';
    input_box.style.border = '1px solid black';
    usersname.disabled = false;
});

//Edit Email for Name
const email = document.querySelector('#email-btn');
email.addEventListener('click', () => {
    const emailid = document.querySelector('#email');
    const input_box = document.querySelector('.emailid input');
    const save = document.querySelector('#save-btn1');
    const cancel = document.querySelector('#cancel-btn1');
    save.style.display = 'block';
    cancel.style.display = 'block';
    input_box.style.border = '1px solid black';
    emailid.disabled = false;
});

//Edit Birthdate for Name
const birthdate = document.querySelector('#birthdate-btn');
birthdate.addEventListener('click', () => {
    const birthdate = document.querySelector('#birthdate');
    const input_box = document.querySelector('.birthdate input');
    const save = document.querySelector('#save-btn2');
    const cancel = document.querySelector('#cancel-btn2');
    save.style.display = 'block';
    cancel.style.display = 'block';
    input_box.style.border = '1px solid black';
    birthdate.disabled = false;
});

//Edit Description for Name
const description = document.querySelector('#description-btn');
description.addEventListener('click', () => {
    const description = document.querySelector('#description');
    const input_box = document.querySelector('.description input');
    const save = document.querySelector('#save-btn3');
    const cancel = document.querySelector('#cancel-btn3');
    save.style.display = 'block';
    cancel.style.display = 'block';
    input_box.style.border = '1px solid black';
    description.disabled = false;
});

// When Cancel button is pressed for Name edit
const cancel = document.querySelector("#cancel-btn");
cancel.addEventListener('click', () => {
    const name = document.querySelector('#name');
    const input_box = document.querySelector('.nickname input');
    const save = document.querySelector('#save-btn');
    const cancel = document.querySelector('#cancel-btn');
    save.style.display = 'none';
    cancel.style.display = 'none'
    input_box.style.border = 'none';
    name.disabled = true;
})

// When Cancel button is pressed for Email edit
const cancel1 = document.querySelector("#cancel-btn1");
cancel1.addEventListener('click', () => {
    const email = document.querySelector('#email');
    const input_box = document.querySelector('.emailid input');
    const save = document.querySelector('#save-btn1');
    const cancel = document.querySelector('#cancel-btn1');
    save.style.display = 'none';
    cancel.style.display = 'none'
    input_box.style.border = 'none';
    email.disabled = true;
})

// When Cancel button is pressed for Birthdate edit
const cancel2 = document.querySelector("#cancel-btn2");
cancel2.addEventListener('click', () => {
    const birthdate = document.querySelector('#birthdate');
    const input_box = document.querySelector('.birthdate input');
    const save = document.querySelector('#save-btn2');
    const cancel = document.querySelector('#cancel-btn2');
    save.style.display = 'none';
    cancel.style.display = 'none'
    input_box.style.border = 'none';
    birthdate.disabled = true;
})

// When Cancel button is pressed for description edit
const cancel3 = document.querySelector("#cancel-btn3");
cancel3.addEventListener('click', () => {
    const description = document.querySelector('#description');
    const input_box = document.querySelector('.description input');
    const save = document.querySelector('#save-btn3');
    const cancel = document.querySelector('#cancel-btn3');
    save.style.display = 'none';
    cancel.style.display = 'none'
    input_box.style.border = 'none';
    description.disabled = true;
})