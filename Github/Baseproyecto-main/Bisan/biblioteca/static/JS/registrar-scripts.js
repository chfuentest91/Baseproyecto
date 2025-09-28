(function ($) {
  'use strict';

  $(function () {
    // ---- CSRF cookie (Django docs pattern) ----
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        for (let c of document.cookie.split(";")) {
          c = c.trim();
          if (c.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(c.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    // ---- Cached elements (all lowercase to match HTML) ----
    const $form = $("#contactForm");
    const $nombre = $("#nombre");
    const $apellidos = $("#apellidos");
    const $email = $("#email");
    const $direccion = $("#direccion");
    const $telefono = $("#telefono");
    const $rol = $("#rol");
    const $clave = $("#clave");
    const $clave2 = $("#clave2");

    // ---- Helpers ----
    function showErr($el, msg) { $el.addClass("is-invalid"); $el.next(".error-message").text(msg).show(); }
    function clrErr($el) { $el.removeClass("is-invalid"); $el.next(".error-message").text("").hide(); }

    $form.on("input change", "input, select", function () { clrErr($(this)); });

    function validaPassword() {
      const pass = $clave.val().trim();
      const pass2 = $clave2.val().trim();
      const re = /^(?=.*[A-Z])(?=.*\d).{6,18}$/;
      let ok = true;

      $("#claveError").text("").hide();
      $("#clave2Error").text("").hide();

      if (!pass) { $("#claveError").text("La contraseña es obligatoria.").show(); ok = false; }
      else if (!re.test(pass)) {
        $("#claveError").text("Debe tener al menos una mayúscula, un número y entre 6 y 18 caracteres.").show();
        ok = false;
      }
      if (!pass2) { $("#clave2Error").text("Repite la contraseña.").show(); ok = false; }
      else if (pass !== pass2) { $("#clave2Error").text("Las contraseñas no coinciden.").show(); ok = false; }

      return ok;
    }

    $("#limpiarBtn").on("click", function () {
      $form[0].reset();
      $(".form-control, .form-select").removeClass("is-invalid");
      $(".error-message").text("").hide();
      $("#claveError,#clave2Error").text("").hide();
    });

    // ---- Submit ----
    $("#contactForm").on("submit", function (e) {
      e.preventDefault();

      const datos = {
        nombre: $("#nombre").val().trim(),
        apellidos: $("#apellidos").val().trim(),
        correo: $("#correo").val().trim().toLowerCase(),
        direccion: $("#direccion").val().trim(),
        telefono: $("#telefono").val().trim(),
        clave: $("#clave").val().trim(),
        rol: parseInt($("#rol").val(), 10)
      };

      $.ajax({
        url: window.REGISTER_URL || "/core/registrar/",
        type: "POST",
        data: JSON.stringify(datos),
        contentType: "application/json",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        dataType: "json",
        success: function (res, textStatus, xhr) {
          if (xhr.status === 201) {
            alert(res.mensaje || "Registrado exitosamente");
            $("#contactForm")[0].reset();
          } else {
            alert(res.error || "Error desconocido");
          }
        },
        error: function (xhr) {
          alert(xhr.responseJSON?.error || "Error al registrar");
        }
      });
    });
  });
})(window.jQuery);
