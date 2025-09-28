$(document).ready(function () {



    $("#contactForm").submit(function (event) {
        event.preventDefault(); // Evita el envío por defecto
        let isValid = true;


        $(".error-message").hide(); // Ocultar mensajes previos
        $(".form-control").removeClass("is-invalid"); // Quitar estilos previos



        // Validar el campo Email (Obligatorio y formato válido)
        let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if ($("#Email").val().trim() === "" || !emailPattern.test($("#Email").val())) {
            $("#Email").addClass("is-invalid");
            $("#Email").next(".error-message").text("Por favor, ingresa un email válido.").show();
            isValid = false;
        }


        // Si todo es válido, mostrar alerta y reiniciar el formulario
        if (isValid) {
            alert("Su contraseña se ha enviado a su correo.");
            $("#contactForm")[0].reset(); // Reiniciar el formulario
        }
    });
});

