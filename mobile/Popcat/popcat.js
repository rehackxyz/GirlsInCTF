Java.perform(() => {
    var MainActivity = Java.use('com.girlsinctf.popcat.MainActivityKt');
    MainActivity.PopcatApp$lambda$5
        .overload('androidx.compose.runtime.MutableState', 'int')
        .implementation = function(state, i) {
            console.log(`[+] State: ${state}`)
            console.log(`[+] i: ${i}`)
            // Modify our score to get flag
            this.PopcatApp$lambda$5(state, 999999999);
        }
})