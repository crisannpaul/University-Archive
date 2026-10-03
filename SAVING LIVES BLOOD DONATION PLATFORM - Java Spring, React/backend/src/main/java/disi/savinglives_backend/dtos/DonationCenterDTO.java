package disi.savinglives_backend.dtos;


import lombok.Data;

import java.util.UUID;

@Data
public class DonationCenterDTO {

    private UUID id;

    private String name;

    private String country;

    private String region;

    private String city;

    private String streetNumber;

    private String street;

    private Double latitude;

    private Double longitude;

    public DonationCenterDTO(UUID id, String name, String country, String region, String city, String streetNumber) {
        this.id = id;
        this.name = name;
        this.country = country;
        this.region = region;
        this.city = city;
        this.streetNumber = streetNumber;
    }

    public DonationCenterDTO(UUID id, String name, String country, String region, String city, String streetNumber, Double latitude, Double longitude) {
        this.id = id;
        this.name = name;
        this.country = country;
        this.region = region;
        this.city = city;
        this.streetNumber = streetNumber;
        this.latitude = latitude;
        this.longitude = longitude;
    }

    public DonationCenterDTO() {
    }
}
