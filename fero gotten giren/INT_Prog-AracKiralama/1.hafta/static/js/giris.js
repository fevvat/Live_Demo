const form = document.getElementById('form');
const firstnameInput = document.getElementById('firstname-input');
const emailInput = document.getElementById('email-input');
const passwordInput = document.getElementById('password-input');
const repeatPassInput = document.getElementById('repeat-password-input');
const error = document.getElementById('error');

let errors = [];

form.addEventListener('submit', (e)=> {
    console.log('im from signup')
    debugger
    if(firstnameInput) {
        // if true, then we are in the signup page
        errors = getSignupFormErrors(firstnameInput.value, emailInput.value, passwordInput.value, repeatPassInput.value);
    } else {
        // we are in the login 
        errors = getLoginFormErrors(emailInput.value, passwordInput.value);
    }

    if(errors.length > 0) {
        e.preventDefault();
        error.innerText = errors.join('\n');
    }
})

function getSignupFormErrors(firstname, email, password, repeatPass) {
    let errors = [];

    if(firstname === '' || firstname === null) {
        errors.push('İsim gereklidir!');
        firstnameInput.parentElement.classList.add('incorrect');
    }

    if(email === '' || email === null) {
        errors.push(' Email gereklidir!');
        emailInput.parentElement.classList.add('incorrect');
    }

    if(password === '' || password === null) {
        errors.push('Şifre gereklidir!');
        passwordInput.parentElement.classList.add('incorrect');
    }

    if(repeatPass !== password || repeatPass === null) {
        errors.push('Şifreler eşleşmiyor!');
        repeatPassInput.parentElement.classList.add('incorrect');
    }

    return errors;
}

function getLoginFormErrors(email, password) {
    let errors = [];

    if(email == '' || email == null) {
        errors.push('E-Posta gereklidir!');
        emailInput.parentElement.classList.add('incorrect');
    }

    if(password == '' || password == null) {
        errors.push('Şifre gereklidir!');
        passwordInput.parentElement.classList.add('incorrect');
    }

    return errors;
}

const allInputs = [firstnameInput, emailInput, passwordInput, repeatPassInput].filter(input => input != null);

allInputs.forEach(input => {
    input.addEventListener('input', ()=> {
        if(input.parentElement.classList.contains('incorrect')){
            input.parentElement.classList.remove('incorrect');
        }
    })
})