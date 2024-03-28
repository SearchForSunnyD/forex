class pageHandler{
    constructor() {
        this.from = document.querySelector('#con-from')
        this.to = document.querySelector("#con-to");
        this.amount = document.querySelector("#currency-amount");
        this.displayBox = document.querySelector("#messages");
		this.form = document.querySelector("#con-form");

        this.amount.addEventListener("change", this.showTwo.bind(this));
        this.form.addEventListener("submit", this.handler.bind(this));
    }

    async handler(evt) {
        evt.preventDefault();
        let from = this.from.value
        let to = this.to.value;
        let amount = this.amount.value;
        let response = await axios.get("/conv", {
			params: { from: from, to: to, amount: amount },
        });
        console.log(response);
        this.displayBox.innerHTML = response.data
    }

    showTwo() {
        this.amount.value = parseFloat(this.amount.value).toFixed(2);
    }

}
