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
            // Aqui acessamos o telefone via extendedProps
            openInfoBox(
                info.event.title,
                "Deseja remover esta consulta?",
                info.event.id,
                info.event.start,
                info.event.extendedProps.phone // Passando o telefone
            );
        },
        eventRender: function(info) {
            info.el.innerHTML = info.event.title; // Exibe apenas o título do evento
        }
    });
  
    calendar.render();

    function openInfoBox(title, details, eventId, eventStart, phone) {
        document.getElementById('info-title').innerText = title;
        document.getElementById('info-details').innerText = details;
    
        const phoneElement = document.getElementById('info-phone');
        if (phone) {
            const sanitizedPhone = phone.replace(/\D/g, ''); // Remove caracteres não numéricos
            const message = `Olá ${title}, aqui é do consultório da Dra. Giovanna. Poderíamos confirmar sua consulta no dia ${eventStart.toLocaleDateString()} às ${eventStart.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}?`;
            const whatsappLink = `https://wa.me/55${sanitizedPhone}?text=${encodeURIComponent(message)}`;
            
            phoneElement.innerHTML = `
                ${phone} 
                (<a href="${whatsappLink}" target="_blank" >WhatsApp</a>)
            `;
        } else {
            phoneElement.innerHTML = 'N/A';
        }
    
        document.getElementById('info-box').style.display = 'block';
        document.getElementById('remove-event').dataset.eventId = eventId;
    
        const eventDate = eventStart.toISOString().split('T')[0]; // Data no formato YYYY-MM-DD
        const eventTime = eventStart.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); // Hora no formato HH:mm
    
        document.getElementById('remove-event').dataset.eventDate = eventDate; // Armazena data no botão
        document.getElementById('remove-event').dataset.eventTime = eventTime; // Armazena hora no botão
    }
  
    // function openInfoBox(title, details, eventId, eventStart, phone) {
    //     document.getElementById('info-title').innerText = title;
    //     document.getElementById('info-details').innerText = details;
    //     document.getElementById('info-phone').innerText = phone || 'N/A';

    //     document.getElementById('info-box').style.display = 'block';
    //     document.getElementById('remove-event').dataset.eventId = eventId;
  
    //     // Extraindo data e hora do evento
    //     const eventDate = eventStart.toISOString().split('T')[0]; // Data no formato YYYY-MM-DD
    //     const eventTime = eventStart.toTimeString().split(' ')[0]; // Hora no formato HH:mm:ss
  
    //     document.getElementById('remove-event').dataset.eventDate = eventDate; // Armazenar data no botão
    //     document.getElementById('remove-event').dataset.eventTime = eventTime; // Armazenar hora no botão
    // }
  
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
                var evt = calendar.getEventById(eventId);
                if(evt) evt.remove();
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
        if (form && form.style.display === 'block' && !form.contains(event.target)) {
            form.style.display = 'none';
        }
    });
  
    // Adiciona evento ao botão de fechar o formulário
    var fecharBtn = document.getElementById('fechar');
    if(fecharBtn){
        fecharBtn.addEventListener('click', function() {
            document.getElementById('form-c').style.display = 'none'; // Oculta a caixa
        });
    }
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

function mascaraTelefone(telefone) {
    let valor = telefone.value;
    valor = valor.replace(/\D/g, ''); // Remove tudo que não for dígito
    valor = valor.replace(/^(\d{2})(\d)/g, "($1) $2"); // Coloca os parênteses no DDD
    valor = valor.replace(/(\d)(\d{4})$/, "$1-$2"); // Coloca o hífen entre o 4º e 5º dígito
    telefone.value = valor;
}



// document.addEventListener('DOMContentLoaded', function() {
//   var calendarEl = document.getElementById('calendar');
//   var calendar = new FullCalendar.Calendar(calendarEl, {
//       initialView: 'dayGridMonth',
//       headerToolbar: {
//           left: 'prev,next today',
//           center: 'title',
//           right: 'dayGridMonth,timeGridWeek,timeGridDay'
//       },
//       locale: 'pt', // Define o idioma como português
//       views: {
//           dayGridMonth: {
//               buttonText: 'Mês'
//           },
//           timeGridWeek: {
//               buttonText: 'Semana'
//           },
//           timeGridDay: {
//               buttonText: 'Dia'
//           }
//       },
//       editable: false,
//       events: '/api/events',
//       dateClick: function(info) {
//           openForm(info.dateStr); // Abre o formulário ao clicar na data
//       },
//       eventClick: function(info) {
//           openInfoBox(info.event.title, "Deseja remover esta consulta?", info.event.id, info.event.start); // Passa a data e hora
//       },
//       eventRender: function(info) {
//           info.el.innerHTML = info.event.title; // Exibe apenas o título do evento
//       }
//   });

//   calendar.render();

//   function openInfoBox(title, details, eventId, eventStart) {
//       document.getElementById('info-title').innerText = title;
//       document.getElementById('info-details').innerText = details;
//       document.getElementById('info-box').style.display = 'block';
//       document.getElementById('remove-event').dataset.eventId = eventId;

//       // Extraindo data e hora do evento
//       const eventDate = eventStart.toISOString().split('T')[0]; // Data no formato YYYY-MM-DD
//       const eventTime = eventStart.toTimeString().split(' ')[0]; // Hora no formato HH:mm:ss

//       document.getElementById('remove-event').dataset.eventDate = eventDate; // Armazenar data no botão
//       document.getElementById('remove-event').dataset.eventTime = eventTime; // Armazenar hora no botão
//   }

//   // Fechar a caixa de informações
//   document.getElementById('close-box').addEventListener('click', function() {
//       document.getElementById('info-box').style.display = 'none';
//   });

//   // Remover o evento ao clicar no botão
//   document.getElementById('remove-event').addEventListener('click', function() {
//       var eventId = this.dataset.eventId; // Obtém o ID do evento
//       var eventDate = this.dataset.eventDate; // Obtém a data do evento
//       var eventTime = this.dataset.eventTime; // Obtém a hora do evento

//       var confirmation = confirm("Tem certeza de que deseja remover esta consulta?");
//       if (confirmation) {
//           fetch(`/api/delete-event/${eventId}`, {
//               method: 'DELETE',
//               headers: {
//                   'Content-Type': 'application/json'
//               },
//               body: JSON.stringify({ date: eventDate, time: eventTime }) // Enviar data e hora no corpo da requisição
//           })
//           .then(response => {
//               if (!response.ok) {
//                   throw new Error('Erro ao deletar evento');
//               }
//               return response.json();
//           })
//           .then(data => {
//               console.log('Evento removido:', data);
//               // Remove visualmente o evento do calendário
//               calendar.getEventById(eventId).remove(); 
//               document.getElementById('info-box').style.display = 'none'; // Oculta a caixa

//               // Recarrega a página para atualizar a lista de eventos
//               window.location.reload();
//           })
//           .catch((error) => {
//               console.error('Erro ao remover o evento:', error);
//           });
//       }
//   });

//   // Fecha o formulário ao clicar fora dele
//   document.addEventListener('click', function(event) {
//       var form = document.getElementById('form-c');
//       if (form.style.display === 'block' && !form.contains(event.target)) {
//           form.style.display = 'none';
//       }
//   });

//   // Adiciona evento ao botão de fechar o formulário
//   document.getElementById('fechar').addEventListener('click', function() {
//       document.getElementById('form-c').style.display = 'none'; // Oculta a caixa
//   });
// });

// function openForm(date) {
//   document.getElementById('form-c').style.display = 'block'; // Mostra o formulário
//   document.getElementById('selected-date').value = date; // Preenche a data no formulário
// }

// function submitForm(event) {
//   event.preventDefault(); // Impede o envio padrão do formulário
//   const formData = new FormData(event.target); // Coleta os dados do formulário
//   fetch('/api/consulta', {
//       method: 'POST',
//       body: formData
//   })
//   .then(response => response.json())
//   .then(data => {
//       console.log('Consulta marcada:', data);
//       window.location.reload(); // Recarrega a página para ver as novas consultas
//   })
//   .catch((error) => {
//       console.error('Erro:', error);
//   });
// }
