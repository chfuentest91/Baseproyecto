// traductor.js
$(document).ready(function () {
  const $form = $("#form-traducir");
  const $alerta = $("#alerta");
  const $resultado = $("#resultado");
  const $textoTrad = $("#texto-traducido");
  const $idiomaOrigen = $("#idioma-origen");
  const $btn = $form.find("button[type=submit]");

  function resetUI() {
    $alerta.addClass("d-none").text("");
    $resultado.addClass("d-none");
    $textoTrad.text("");
    $idiomaOrigen.text("");
  }

  $form.on("submit", function (e) {
    e.preventDefault();
    resetUI();

    const payload = {
      texto: $("#texto").val(),
      origen: $("#origen").val(),
      destino: $("#destino").val(),
    };

    // estado cargando
    $btn.prop("disabled", true).data("old", $btn.text()).text("Traduciendo...");

    $.ajax({
      url: "/api/traducir/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      // Si QUITAS @csrf_exempt en la vista, descomenta esta línea para enviar el token:
      // headers: { "X-CSRFToken": getCookie("csrftoken") }
    })
      .done(function (data) {
        $textoTrad.text(data.traduccion || "(sin resultado)");
        if (data.origen_detectado) {
          $idiomaOrigen.text("Idioma detectado: " + data.origen_detectado);
        }
        $resultado.removeClass("d-none");
      })
      .fail(function (xhr) {
        let msg = "Error al traducir.";
        try {
          const j = JSON.parse(xhr.responseText);
          if (j.error) msg = j.error;
        } catch (_) {}
        $alerta.removeClass("d-none").text(msg);
      })
      .always(function () {
        $btn.prop("disabled", false).text($btn.data("old") || "Traducir");
      });
  });

  // --- Utilidad para CSRF si decides habilitarlo en la vista (quitar @csrf_exempt) ---
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
  }
});
