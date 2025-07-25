function updateStatus(complaintId, newStatus) {
  fetch(`/admin/update_status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ id: complaintId, status: newStatus }),
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Status updated!");
      location.reload();
    } else {
      alert("Failed to update.");
    }
  });
}
