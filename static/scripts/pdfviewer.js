fetch('/json')
    .then(response => response.json())
    .then(data => {
      const url = data['key1'];
      console.log(data);
      let pdfDoc = null,
      pageNum = 1,
      pageIsRendering = false,
      pageNumIsPending = null;

  const scale = 1.4,
      canvas = document.querySelector('#pdf-render'),
      ctx = canvas.getContext('2d'),
      pageInput = document.getElementById('page-input'),
      goButton = document.getElementById('go-button');


  const renderPage = num => {
      pageIsRendering = true

      pdfDoc.getPage(num).then(page => {
          // Set scale
          const viewport = page.getViewport({ scale });
          canvas.height = viewport.height;
          canvas.width = viewport.width;
      
          const renderCtx = {
            canvasContext: ctx,
            viewport
          };
      
          page.render(renderCtx).promise.then(() => {
            pageIsRendering = false;
      
            if (pageNumIsPending !== null) {
              renderPage(pageNumIsPending);
              pageNumIsPending = null;
            }
          });
          // Output current page
          document.querySelector('#page-input').value = num;
          document.querySelector('#page-num').textContent = num;
      });
  };

  // Check for pages rendering
  const queueRenderPage = num => {
      if (pageIsRendering) {
        pageNumIsPending = num;
      } else {
        renderPage(num);
      }
  };
    
    // Show Prev Page
    const showPrevPage = () => {
      if (pageNum <= 1) {
        return;
      }
      pageNum--;
      queueRenderPage(pageNum);
      };
    
    // Show Next Page
    const showNextPage = () => {
      if (pageNum >= pdfDoc.numPages) {
        return;
      }
      pageNum++;
      queueRenderPage(pageNum);
      };

  // Функция для перехода к выбранной странице
  function goToPage() {
      var pageNumber = parseInt(pageInput.value, 10);
      if (pageNumber >= 1 && pageNumber <= pdfDoc.numPages) {
        pageNum = pageNumber;
        renderPage(pageNum);
      }
    }

    // Обработчик события клика на кнопке "Перейти"
    goButton.addEventListener('click', goToPage);

  //Get doc
  pdfjsLib.getDocument(url).promise.then(pdfDoc_ => {
      pdfDoc = pdfDoc_;

      document.querySelector('#page-count').textContent = pdfDoc.numPages;

      renderPage(pageNum)
  });

  // Button Events
  document.querySelector('#prev-page').addEventListener('click', showPrevPage);
  document.querySelector('#next-page').addEventListener('click', showNextPage);
});
