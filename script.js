<script>
  $(document).foundation({
    tab: {
      callback : function (tab) {
        console.log(tab);
      }
    }
  });
</script>

<script>
  $('#myTabs').on('toggled', function (event, tab) {
    console.log(tab);
  });
</script>

