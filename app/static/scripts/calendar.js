document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      locale: 'pt', // Define o idioma como português
      views: {
          dayGridMonth: {
              buttonText: 'Mês'
          },
          timeGridWeek: {
              buttonText: 'Semana'
          },
          timeGridDay: {
              buttonText: 'Dia'
          }
      },
      editable: false,
      events: '/api/events',
      dateClick: function(info) {
          openForm(info.dateStr); // Abre o formulário ao clicar na data
      },
      eventClick: function(info) {
          openInfoBox(info.event.title, "Deseja remover esta consulta?", info.event.id, info.event.start); // Passa a data e hora
      },
      eventRender: function(info) {
          info.el.innerHTML = info.event.title; // Exibe apenas o título do evento
      }
  });

  calendar.render();

  function openInfoBox(title, details, eventId, eventStart) {
      document.getElementById('info-title').innerText = title;
      document.getElementById('info-details').innerText = details;
      document.getElementById('info-box').style.display = 'block';
      document.getElementById('remove-event').dataset.eventId = eventId;

      // Extraindo data e hora do evento
      const eventDate = eventStart.toISOString().split('T')[0]; // Data no formato YYYY-MM-DD
      const eventTime = eventStart.toTimeString().split(' ')[0]; // Hora no formato HH:mm:ss

      document.getElementById('remove-event').dataset.eventDate = eventDate; // Armazenar data no botão
      document.getElementById('remove-event').dataset.eventTime = eventTime; // Armazenar hora no botão
  }

  // Fechar a caixa de informações
  document.getElementById('close-box').addEventListener('click', function() {
      document.getElementById('info-box').style.display = 'none';
  });

  // Remover o evento ao clicar no botão
  document.getElementById('remove-event').addEventListener('click', function() {
      var eventId = this.dataset.eventId; // Obtém o ID do evento
      var eventDate = this.dataset.eventDate; // Obtém a data do evento
      var eventTime = this.dataset.eventTime; // Obtém a hora do evento

      var confirmation = confirm("Tem certeza de que deseja remover esta consulta?");
      if (confirmation) {
          fetch(`/api/delete-event/${eventId}`, {
              method: 'DELETE',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ date: eventDate, time: eventTime }) // Enviar data e hora no corpo da requisição
          })
          .then(response => {
              if (!response.ok) {
                  throw new Error('Erro ao deletar evento');
              }
              return response.json();
          })
          .then(data => {
              console.log('Evento removido:', data);
              // Remove visualmente o evento do calendário
              calendar.getEventById(eventId).remove(); 
              document.getElementById('info-box').style.display = 'none'; // Oculta a caixa

              // Recarrega a página para atualizar a lista de eventos
              window.location.reload();
          })
          .catch((error) => {
              console.error('Erro ao remover o evento:', error);
          });
      }
  });

  // Fecha o formulário ao clicar fora dele
  document.addEventListener('click', function(event) {
      var form = document.getElementById('form-c');
      if (form.style.display === 'block' && !form.contains(event.target)) {
          form.style.display = 'none';
      }
  });

  // Adiciona evento ao botão de fechar o formulário
  document.getElementById('fechar').addEventListener('click', function() {
      document.getElementById('form-c').style.display = 'none'; // Oculta a caixa
  });
});

function openForm(date) {
  document.getElementById('form-c').style.display = 'block'; // Mostra o formulário
  document.getElementById('selected-date').value = date; // Preenche a data no formulário
}

function submitForm(event) {
  event.preventDefault(); // Impede o envio padrão do formulário
  const formData = new FormData(event.target); // Coleta os dados do formulário
  fetch('/api/consulta', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      console.log('Consulta marcada:', data);
      window.location.reload(); // Recarrega a página para ver as novas consultas
  })
  .catch((error) => {
      console.error('Erro:', error);
  });
}
