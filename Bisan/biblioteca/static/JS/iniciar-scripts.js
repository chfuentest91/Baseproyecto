(function ($) {
  'use strict';
  if (!$) { console.error('jQuery no cargó'); return; }

  $(function () {
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let c of cookies) {
          c = c.trim();
          if (c.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(c.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const csrftoken =
      getCookie("csrftoken") ||
      (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value ||
      "";


    const EXPLICIT_ERR = {
      ClaveLogin: $("#claveError")
    };

    function getErrorBox($el) {
      let $box = $el.next(".error-message");
      if ($box.length) return $box;
      $box = $el.siblings(".error-message");
      if ($box.length) return $box;
      const id = $el.attr("id");
      if (id && EXPLICIT_ERR[id] && EXPLICIT_ERR[id].length) return EXPLICIT_ERR[id];
      $box = $('<div class="error-message text-danger"></div>');
      $el.after($box);
      return $box;
    }

    function showFieldError($el, msg) {
      $el.addClass("is-invalid");
      const $box = getErrorBox($el);
      $box.text(msg).show();
    }

    function clearFieldError($el) {
      $el.removeClass("is-invalid");
      const $box = getErrorBox($el);
      $box.text("").hide();
    }

    // Limpiar errores en input
    $("#EmailLogin, #ClaveLogin").on("input", function () {
      clearFieldError($(this));
      $("#loginError").hide().text("");
    });

    // =============== Submit ===============
    $("#loginForm").on("submit", function (e) {
      e.preventDefault();

      let ok = true;
      $(".error-message").hide();
      $(".form-control, .form-select").removeClass("is-invalid");

      const $Email = $("#EmailLogin");
      const $Clave = $("#ClaveLogin");
      const $Btn = $(this).find('button[type="submit"]');

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if ($Email.val().trim() === "" || !emailRegex.test($Email.val().trim())) {
        showFieldError($Email, "Ingresa un correo válido.");
        ok = false;
      }
      if (!$Clave.val() || $Clave.val().trim() === "") {
        showFieldError($Clave, "La contraseña es obligatoria.");
        ok = false;
      }
      if (!ok) return;

      const payload = {
        correo: $Email.val().trim().toLowerCase(),
        clave: $Clave.val().trim()
      };

      const LOGIN_URL = window.LOGIN_URL || "/core/login/";

      // Evitar doble submit
      const originalText = $Btn.text();
      $Btn.prop("disabled", true).text("Ingresando...");

      $.ajax({
        url: LOGIN_URL,
        type: "POST",
        data: JSON.stringify(payload),
        contentType: "application/json",
        headers: { "X-CSRFToken": csrftoken },

        success: function (res) {
          // Si el backend reporta fallo 
          if (res && res.success === false) {
            $("#loginError").text(res.error || "No se pudo iniciar sesión.").show();
            $Btn.prop("disabled", false).text(originalText);
            return;
          }

          if (res && res.next_url) {
            window.location.assign(res.next_url);
            return;
          }

          const rolNombre = (res && res.rol ? String(res.rol) : "").toLowerCase();
          const redirects = {
            superusuario: "/core/admin/",
            administrador: "/core/admin/",
            invitado: "/",
            profesor: "/core/profesor/",
            alumno: "/core/alumno/"
          };
          const destino = redirects[rolNombre] || "/";
          window.location.assign(destino);
        },

        error: function (xhr) {
          const msg = xhr.responseJSON?.error || "Error al iniciar sesión.";
          $("#loginError").text(msg).show();
          $Btn.prop("disabled", false).text(originalText);
        }
      });
    });
  });
})(window.jQuery);
