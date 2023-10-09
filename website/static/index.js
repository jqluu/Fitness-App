function deleteWeight(weightId) {
    fetch("/delete-weight", {
      method: "POST",
      body: JSON.stringify({ weightId: weightId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }