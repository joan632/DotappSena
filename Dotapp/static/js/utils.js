/**
 * Utilidades JavaScript para DotApp SENA
 * 
 * Este archivo contiene funciones auxiliares utilizadas en toda la aplicación,
 * incluyendo manejo de cookies, notificaciones y cambio de temas.
 */

/**
 * Obtiene el valor de una cookie por su nombre.
 * 
 * Esta función busca en todas las cookies del documento y retorna el valor
 * de la cookie que coincida con el nombre proporcionado. Es útil para obtener
 * tokens CSRF y otros valores almacenados en cookies.
 * 
 * @param {string} name - Nombre de la cookie a buscar
 * @returns {string|null} - Valor de la cookie o null si no se encuentra
 * 
 * @example
 * const csrfToken = getCookie('csrftoken');
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Muestra una notificación en la interfaz de usuario.
 * 
 * Crea y muestra una notificación temporal en la página. La notificación
 * aparece con una animación, se muestra durante 3 segundos y luego se
 * desvanece automáticamente. Si no existe un contenedor de notificaciones,
 * lo crea automáticamente.
 * 
 * @param {string} message - Mensaje a mostrar en la notificación
 * @param {string} [type='info'] - Tipo de notificación (info, success, warning, error)
 * 
 * @example
 * showNotification('Operación exitosa', 'success');
 * showNotification('Error al procesar', 'error');
 */
function showNotification(message, type = 'info') {
  let container = document.querySelector('.notifications');

  if (!container) {
    container = document.createElement('div');
    container.className = 'notifications';
    document.body.appendChild(container);
  }

  const n = document.createElement('div');
  n.className = `notification ${type}`;
  n.textContent = message;
  container.appendChild(n);

  // Animación de aparición
  requestAnimationFrame(() => n.classList.add('show'));

  // Desvanecer y eliminar después de 3 segundos
  setTimeout(() => {
    n.classList.remove('show');
    setTimeout(() => n.remove(), 500);
  }, 3000);
}

/**
 * Guarda una notificación en sessionStorage y recarga la página.
 * 
 * Útil para mostrar mensajes después de una redirección o recarga de página.
 * La notificación se almacena temporalmente y se muestra automáticamente
 * cuando la página se carga nuevamente.
 * 
 * @param {string} message - Mensaje a mostrar después del reload
 * @param {string} [type='info'] - Tipo de notificación
 * 
 * @example
 * saveAndReload('Cambios guardados correctamente', 'success');
 */
function saveAndReload(message, type = 'info') {
  sessionStorage.setItem('pendingNotification', JSON.stringify({ message, type }));
  location.reload();
}

/**
 * Muestra notificaciones pendientes al cargar la página.
 * 
 * Event listener que se ejecuta cuando el DOM está listo. Verifica si hay
 * notificaciones guardadas en sessionStorage y las muestra automáticamente.
 * Esto permite mostrar mensajes después de redirecciones o recargas.
 */
document.addEventListener('DOMContentLoaded', () => {
  const pending = sessionStorage.getItem('pendingNotification');
  if (pending) {
    const { message, type } = JSON.parse(pending);
    showNotification(message, type);
    sessionStorage.removeItem('pendingNotification');
  }
});

/**
 * Desvanece automáticamente las notificaciones existentes en el DOM.
 * 
 * Cuando la página carga, busca todas las notificaciones que ya están
 * presentes en el HTML (por ejemplo, desde el sistema de mensajes de Django)
 * y las desvanece automáticamente después de 3 segundos.
 */
document.addEventListener("DOMContentLoaded", () => {
  const notifs = document.querySelectorAll(".notification");
  notifs.forEach(n => {
    setTimeout(() => {
      void n.offsetWidth; // Forzar repintado para activar la transición
      n.style.opacity = "0";
      setTimeout(() => n.remove(), 500);
    }, 3000);
  });
});


/**
 * Sistema de cambio de temas (Theme Toggle).
 * 
 * Implementa un sistema de cambio de temas visuales para la aplicación.
 * Permite al usuario alternar entre diferentes paletas de colores predefinidas.
 * La preferencia del usuario se guarda en localStorage para persistir entre sesiones.
 * 
 * Temas disponibles:
 * - aqua: Tema acuático (por defecto)
 * - dark: Tema oscuro
 * - emerald: Tema esmeralda
 * - sunset: Tema atardecer
 * - purple: Tema morado
 * - mono: Tema monocromático
 * 
 * @function
 * @returns {void}
 */
(() => {
  const palettes = [
    'aqua', 'dark', 'emerald', 'sunset', 'purple', 'mono'
  ];
  
  let idx = 0;

  /**
   * Aplica un tema específico a la página.
   * 
   * Cambia la clase del elemento raíz del documento y guarda la preferencia
   * en localStorage para que persista entre sesiones.
   * 
   * @param {string} name - Nombre del tema a aplicar
   */
  const apply = name => {
    document.documentElement.className = `theme-${name}`;
    localStorage.setItem('dotapp-theme', name);
  };

  // Cargar el tema guardado o usar 'aqua' por defecto
  const saved = localStorage.getItem('dotapp-theme') || 'aqua';
  apply(saved);

  // Configurar el evento click en el botón de cambio de tema
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    idx = (idx + 1) % palettes.length;
    apply(palettes[idx]);
  });
})();
